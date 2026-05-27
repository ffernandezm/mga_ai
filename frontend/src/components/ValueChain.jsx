// ValueChain.jsx
import React, { useState, useEffect } from "react";
import api from "../services/api";
import { useNotification } from "../context/NotificationContext";
import productsCatalogCsv from "../data/products_catalog.csv?raw";

const ValueChain = ({ projectId }) => {
    const { showSuccess, showError, showConfirmation } = useNotification();
    const [objectives, setObjectives] = useState([]);
    const [loading, setLoading] = useState(true);
    const [savingId, setSavingId] = useState(null);

    // Estado para el sector del proyecto y el catálogo de productos
    const [projectSector, setProjectSector] = useState(null);
    const [catalogProducts, setCatalogProducts] = useState([]); // { productName, description, measuredThrough }
    const [loadingCatalog, setLoadingCatalog] = useState(true);

    // 1. Obtener el sector del proyecto actual
    useEffect(() => {
        if (projectId) {
            const fetchProjectSector = async () => {
                try {
                    const res = await api.get(`/projects/${projectId}`);
                    // Asumiendo que el proyecto tiene un campo 'sector'
                    setProjectSector(res.data.sector);
                } catch (error) {
                    console.error("Error al obtener el sector del proyecto:", error);
                }
            };
            fetchProjectSector();
        }
    }, [projectId]);

    // 2. Cargar y parsear el catálogo de productos (una sola vez)
    useEffect(() => {
        const parseCatalog = () => {
            try {
                const lines = productsCatalogCsv.split(/\r?\n/).filter(line => line.trim() !== "");
                if (lines.length <= 1) {
                    setCatalogProducts([]);
                    setLoadingCatalog(false);
                    return;
                }

                // Obtener encabezados (primera línea)
                const headers = lines[0].split(";").map(h => h.trim());
                // Índices de columnas relevantes
                const idxSector = headers.findIndex(h => h === "Sector");
                const idxNombreSector = headers.findIndex(h => h === "Nombre  Sector");
                const idxProducto = headers.findIndex(h => h === "Producto");
                const idxDescripcion = headers.findIndex(h => h === "Descripcion");
                const idxMedido = headers.findIndex(h => h === "Medido a través de");

                const productsMap = new Map(); // para evitar duplicados por nombre de producto

                for (let i = 1; i < lines.length; i++) {
                    const values = lines[i].split(";").map(v => v.trim());
                    const codSector = values[idxSector];
                    const nombreSector = values[idxNombreSector];
                    const productName = values[idxProducto];
                    const description = values[idxDescripcion];
                    const measuredThrough = values[idxMedido];

                    if (!productName) continue;

                    // Guardar la primera aparición de cada producto (no duplicados)
                    if (!productsMap.has(productName)) {
                        productsMap.set(productName, {
                            productName,
                            description,
                            measuredThrough,
                            sectorCod: codSector,
                            sectorNombre: nombreSector,
                        });
                    }
                }

                setCatalogProducts(Array.from(productsMap.values()));
            } catch (error) {
                console.error("Error parseando catálogo de productos:", error);
                setCatalogProducts([]);
            } finally {
                setLoadingCatalog(false);
            }
        };
        parseCatalog();
    }, []);

    // 3. Obtener los productos del catálogo filtrados por el sector del proyecto
    const filteredProducts = React.useMemo(() => {
        if (!projectSector || !catalogProducts.length) return [];
        // Comparar con código de sector o nombre de sector (insensible a mayúsculas/minúsculas)
        const sectorNormalized = projectSector.toString().trim().toLowerCase();
        return catalogProducts.filter(prod =>
            prod.sectorCod?.toLowerCase() === sectorNormalized ||
            prod.sectorNombre?.toLowerCase() === sectorNormalized
        );
    }, [projectSector, catalogProducts]);

    // Mapa para obtener descripción y medida a partir del nombre del producto
    const productDetailsMap = React.useMemo(() => {
        const map = new Map();
        filteredProducts.forEach(prod => {
            map.set(prod.productName, {
                description: prod.description,
                measuredThrough: prod.measuredThrough
            });
        });
        return map;
    }, [filteredProducts]);

    // 4. Cargar datos de la cadena de valor (objetivos, productos, actividades)
    const fetchData = async () => {
        try {
            setLoading(true);
            const resObjectives = await api.get(`/value_chain_objectives/`);
            const projectObjectives = resObjectives.data.filter(obj => obj.project_id === parseInt(projectId));

            const fullData = await Promise.all(projectObjectives.map(async (obj) => {
                const resProducts = await api.get(`/products/`);
                const products = resProducts.data.filter(p => p.value_chain_objective_id === obj.id);

                const productsWithActivities = await Promise.all(products.map(async (prod) => {
                    const resActs = await api.get(`/activities/`);
                    const activities = resActs.data.filter(a => a.product_id === prod.id);
                    return { ...prod, activities };
                }));

                return { ...obj, products: productsWithActivities };
            }));

            setObjectives(fullData);
        } catch (error) {
            console.error("Error cargando cadena de valor:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (projectId) {
            fetchData();
        }
    }, [projectId]);

    // Manejo de cambios en el selector de producto (nombre del producto)
    const handleProductSelection = (objId, prodId, selectedProductName) => {
        const details = productDetailsMap.get(selectedProductName);
        if (details) {
            setObjectives(prev => prev.map(obj => {
                if (obj.id !== objId) return obj;
                return {
                    ...obj,
                    products: obj.products.map(p =>
                        p.id === prodId
                            ? {
                                ...p,
                                description: details.description,
                                measured_through: details.measuredThrough
                            }
                            : p
                    )
                };
            }));
        }
    };

    // Resto de handlers (sin cambios relevantes)
    const handleActivityChange = (objId, prodId, actId, field, value) => {
        setObjectives(prev => prev.map(obj => {
            if (obj.id !== objId) return obj;
            return {
                ...obj,
                products: obj.products.map(p => {
                    if (p.id !== prodId) return p;
                    return {
                        ...p,
                        activities: p.activities.map(a =>
                            a.id === actId ? { ...a, [field]: value } : a
                        )
                    };
                })
            };
        }));
    };

    const handleSaveEverything = async (product) => {
        setSavingId(product.id);
        try {
            const productData = {
                project_id: product.project_id,
                value_chain_objective_id: product.value_chain_objective_id,
                description: product.description || "",
                measured_through: product.measured_through || "",
                quantity: parseFloat(product.quantity) || 0,
                cost: parseFloat(product.cost) || 0,
                stage: product.stage || "Preinversión"
            };
            await api.put(`/products/${product.id}`, productData);

            const activityPromises = product.activities.map(act => {
                const actData = {
                    project_id: act.project_id,
                    product_id: act.product_id,
                    description: act.description || "",
                    cost: parseFloat(act.cost) || 0,
                    stage: act.stage || "Ejecución"
                };
                return api.put(`/activities/${act.id}`, actData);
            });

            await Promise.all(activityPromises);
            showSuccess("¡Cambios guardados con éxito!");
        } catch (error) {
            console.error("Error al guardar:", error);
            showError("Error al actualizar los datos.");
        } finally {
            setSavingId(null);
        }
    };

    const handleAddProduct = async (objectiveId) => {
        const newProduct = {
            project_id: parseInt(projectId),
            value_chain_objective_id: objectiveId,
            description: "",
            measured_through: "",
            quantity: 0,
            cost: 0,
            stage: "Preinversión"
        };
        await api.post("/products/", newProduct);
        fetchData();
    };

    const handleAddActivity = async (productId) => {
        const newActivity = {
            project_id: parseInt(projectId),
            product_id: productId,
            description: "Nueva Actividad",
            cost: 0,
            stage: "Ejecución"
        };
        await api.post("/activities/", newActivity);
        fetchData();
    };

    const handleDeleteProduct = async (id) => {
        const confirmed = await showConfirmation({
            title: "Eliminar Producto",
            message: "¿Eliminar este producto y sus actividades?"
        });
        if (confirmed) {
            await api.delete(`/products/${id}`);
            fetchData();
            showSuccess("Producto eliminado.");
        }
    };

    const handleDeleteActivity = async (id) => {
        await api.delete(`/activities/${id}`);
        fetchData();
    };

    // Determina qué producto está seleccionado actualmente basado en la descripción
    const getSelectedProductName = (productDescription) => {
        const entry = filteredProducts.find(p => p.description === productDescription);
        return entry ? entry.productName : "";
    };

    if (loading || loadingCatalog) return <div className="text-center p-5 fw-bold text-primary">Cargando datos...</div>;
    if (!projectSector) return <div className="alert alert-warning">No se pudo determinar el sector del proyecto.</div>;
    if (filteredProducts.length === 0) return <div className="alert alert-warning">No hay productos disponibles en el catálogo para el sector "{projectSector}".</div>;

    return (
        <div className="container-fluid py-3">
            <div className="d-flex justify-content-between align-items-center mb-4 bg-white p-3 rounded shadow-sm border">
                <div>
                    <h4 className="text-primary mb-0 fw-bold">Cadena de Valor</h4>
                    <small className="text-muted">Gestión de productos y actividades por objetivo</small>
                </div>
                <button className="btn btn-sm btn-primary" onClick={fetchData}>
                    Sincronizar
                </button>
            </div>

            {objectives.map((obj) => (
                <div key={obj.id} className="card mb-5 border-0 shadow-sm overflow-hidden border">
                    <div className="card-header bg-dark text-white p-3">
                        <div className="d-flex justify-content-between align-items-center">
                            <h5 className="mb-0 small fw-bold text-uppercase">
                                Objetivo: {obj.name}
                            </h5>
                            <button className="btn btn-success btn-sm fw-bold" onClick={() => handleAddProduct(obj.id)}>
                                Nuevo Producto
                            </button>
                        </div>
                    </div>

                    <div className="card-body p-4 bg-light">
                        {obj.products.map((prod) => (
                            <div key={prod.id} className="row mb-4 bg-white rounded-3 shadow-sm mx-0 border overflow-hidden">
                                {/* COLUMNA IZQUIERDA: PRODUCTO */}
                                <div className="col-md-5 p-4 border-end">
                                    <div className="d-flex justify-content-between align-items-start mb-2">
                                        <div className="flex-grow-1">
                                            <label className="text-uppercase fw-bold text-success d-block mb-1 small">
                                                Nombre del Producto
                                            </label>
                                            <select
                                                className="form-select"
                                                value={getSelectedProductName(prod.description)}
                                                onChange={(e) => handleProductSelection(obj.id, prod.id, e.target.value)}
                                            >
                                                <option value="">-- Seleccione un producto --</option>
                                                {filteredProducts.map(p => (
                                                    <option key={p.productName} value={p.productName}>
                                                        {p.productName}
                                                    </option>
                                                ))}
                                            </select>
                                        </div>
                                        <button className="btn btn-sm btn-danger ms-2" onClick={() => handleDeleteProduct(prod.id)}>
                                            Eliminar
                                        </button>
                                    </div>

                                    <div className="row g-2 p-3 rounded bg-light border">
                                        <div className="col-12">
                                            <label className="small text-muted fw-bold mb-1">Descripción</label>
                                            <textarea
                                                className="form-control"
                                                rows="2"
                                                readOnly
                                                value={prod.description || ""}
                                                style={{ backgroundColor: "#f8f9fa" }}
                                            />
                                        </div>
                                        <div className="col-12">
                                            <label className="small text-muted fw-bold mb-1">Medido a través de:</label>
                                            <input
                                                type="text"
                                                className="form-control"
                                                readOnly
                                                value={prod.measured_through || ""}
                                                style={{ backgroundColor: "#f8f9fa" }}
                                            />
                                        </div>
                                        <div className="col-6">
                                            <label className="small text-muted fw-bold mb-1">Cantidad</label>
                                            <input
                                                type="number"
                                                className="form-control form-control-sm"
                                                value={prod.quantity || 0}
                                                onChange={(e) => {
                                                    const newQuantity = parseFloat(e.target.value) || 0;
                                                    setObjectives(prev => prev.map(o => {
                                                        if (o.id !== obj.id) return o;
                                                        return {
                                                            ...o,
                                                            products: o.products.map(p =>
                                                                p.id === prod.id ? { ...p, quantity: newQuantity } : p
                                                            )
                                                        };
                                                    }));
                                                }}
                                            />
                                        </div>
                                        <div className="col-6">
                                            <label className="small text-muted fw-bold mb-1">Costo Unitario</label>
                                            <input
                                                type="number"
                                                className="form-control form-control-sm"
                                                value={prod.cost || 0}
                                                onChange={(e) => {
                                                    const newCost = parseFloat(e.target.value) || 0;
                                                    setObjectives(prev => prev.map(o => {
                                                        if (o.id !== obj.id) return o;
                                                        return {
                                                            ...o,
                                                            products: o.products.map(p =>
                                                                p.id === prod.id ? { ...p, cost: newCost } : p
                                                            )
                                                        };
                                                    }));
                                                }}
                                            />
                                        </div>
                                        <div className="col-12">
                                            <label className="small text-muted fw-bold mb-1">Etapa</label>
                                            <select
                                                className="form-select form-select-sm"
                                                value={prod.stage || "Preinversión"}
                                                onChange={(e) => {
                                                    setObjectives(prev => prev.map(o => {
                                                        if (o.id !== obj.id) return o;
                                                        return {
                                                            ...o,
                                                            products: o.products.map(p =>
                                                                p.id === prod.id ? { ...p, stage: e.target.value } : p
                                                            )
                                                        };
                                                    }));
                                                }}
                                            >
                                                <option value="Preinversión">Preinversión</option>
                                                <option value="Ejecución">Ejecución</option>
                                                <option value="Operación">Operación</option>
                                            </select>
                                        </div>
                                    </div>
                                </div>

                                {/* COLUMNA DERECHA: ACTIVIDADES (sin cambios) */}
                                <div className="col-md-7 p-4 bg-white">
                                    <div className="d-flex justify-content-between align-items-center mb-3">
                                        <h6 className="text-secondary fw-bold mb-0">Actividades Relacionadas</h6>
                                        <button className="btn btn-success btn-sm" onClick={() => handleAddActivity(prod.id)}>
                                            Agregar Actividad
                                        </button>
                                    </div>
                                    <div className="table-responsive">
                                        <table className="table table-striped table-bordered mb-0">
                                            <thead className="table-dark">
                                                <tr>
                                                    <th className="ps-2">Descripción de Actividad</th>
                                                    <th>Costo</th>
                                                    <th>Etapa</th>
                                                    <th style={{ width: "60px" }}>Acciones</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {prod.activities.map((act) => (
                                                    <tr key={act.id} className="align-middle">
                                                        <td>
                                                            <input
                                                                type="text"
                                                                className="form-control form-control-sm border-0 bg-transparent"
                                                                placeholder="Nombre de la actividad..."
                                                                value={act.description || ""}
                                                                onChange={(e) => handleActivityChange(obj.id, prod.id, act.id, 'description', e.target.value)}
                                                            />
                                                        </td>
                                                        <td>
                                                            <input
                                                                type="number"
                                                                className="form-control form-control-sm border-0 bg-transparent"
                                                                style={{ width: "90px" }}
                                                                value={act.cost || 0}
                                                                onChange={(e) => handleActivityChange(obj.id, prod.id, act.id, 'cost', e.target.value)}
                                                            />
                                                        </td>
                                                        <td>
                                                            <select
                                                                className="form-select form-select-sm border-0 bg-transparent"
                                                                value={act.stage || "Ejecución"}
                                                                onChange={(e) => handleActivityChange(obj.id, prod.id, act.id, 'stage', e.target.value)}
                                                            >
                                                                <option value="Preinversión">Preinversión</option>
                                                                <option value="Ejecución">Ejecución</option>
                                                            </select>
                                                        </td>
                                                        <td className="text-center">
                                                            <button className="btn btn-sm btn-danger" onClick={() => handleDeleteActivity(act.id)}>
                                                                Eliminar
                                                            </button>
                                                        </td>
                                                    </tr>
                                                ))}
                                                {prod.activities.length === 0 && (
                                                    <tr>
                                                        <td colSpan="4" className="text-center py-3 text-muted small">
                                                            No hay actividades registradas.
                                                        </td>
                                                    </tr>
                                                )}
                                            </tbody>
                                        </table>
                                    </div>
                                    <div className="mt-3 text-end">
                                        <button
                                            className="btn btn-primary btn-sm fw-bold px-4"
                                            onClick={() => handleSaveEverything(prod)}
                                            disabled={savingId === prod.id}
                                        >
                                            {savingId === prod.id ? "Guardando..." : "Guardar Cambios"}
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            ))}
        </div>
    );
};

export default ValueChain;