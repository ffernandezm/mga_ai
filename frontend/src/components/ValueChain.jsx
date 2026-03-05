import React, { useState, useEffect } from "react";
import api from "../services/api";
import { Plus, Trash2, Save, RefreshCw } from "lucide-react";

const ValueChain = ({ projectId }) => {
    const [objectives, setObjectives] = useState([]);
    const [loading, setLoading] = useState(true);
    const [savingId, setSavingId] = useState(null); // Para mostrar feedback de guardado

    useEffect(() => {
        fetchData();
    }, [projectId]);

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

    // --- Manejadores de Cambio Local (Sincronizan el Input con el Estado) ---
    const handleProductChange = (objId, prodId, field, value) => {
        setObjectives(prev => prev.map(obj => {
            if (obj.id !== objId) return obj;
            return {
                ...obj,
                products: obj.products.map(p =>
                    p.id === prodId ? { ...p, [field]: value } : p
                )
            };
        }));
    };

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

    // --- Función Principal: GUARDAR TODO ---
    const handleSaveEverything = async (objId, product) => {
        setSavingId(product.id);
        try {
            // 1. Actualizar el Producto
            const productData = {
                project_id: product.project_id,
                value_chain_objective_id: product.value_chain_objective_id,
                measured_through: product.measured_through,
                quantity: parseFloat(product.quantity),
                cost: parseFloat(product.cost),
                stage: product.stage
            };
            await api.put(`/products/${product.id}`, productData);

            // 2. Actualizar todas las Actividades de ese producto
            const activityPromises = product.activities.map(act => {
                const actData = {
                    project_id: act.project_id,
                    product_id: act.product_id,
                    cost: parseFloat(act.cost),
                    stage: act.stage
                };
                return api.put(`/activities/${act.id}`, actData);
            });

            await Promise.all(activityPromises);

            alert("¡Información actualizada correctamente!");
        } catch (error) {
            console.error("Error al guardar:", error);
            alert("Hubo un error al guardar los cambios.");
        } finally {
            setSavingId(null);
        }
    };

    // --- Funciones CRUD (Crear/Eliminar) ---
    const handleAddProduct = async (objectiveId) => {
        const newProduct = {
            project_id: parseInt(projectId),
            value_chain_objective_id: objectiveId,
            measured_through: "", quantity: 0, cost: 0, stage: "Planeación"
        };
        await api.post("/products/", newProduct);
        fetchData();
    };

    const handleDeleteProduct = async (id) => {
        if (window.confirm("¿Eliminar producto y sus actividades?")) {
            await api.delete(`/products/${id}`);
            fetchData();
        }
    };

    const handleAddActivity = async (productId) => {
        const newActivity = {
            project_id: parseInt(projectId),
            product_id: productId,
            cost: 0, stage: "Ejecución"
        };
        await api.post("/activities/", newActivity);
        fetchData();
    };

    const handleDeleteActivity = async (id) => {
        await api.delete(`/activities/${id}`);
        fetchData();
    };

    if (loading) return <div className="text-center p-5 fw-bold">Cargando Cadena de Valor...</div>;

    return (
        <div className="container-fluid py-3">
            <div className="d-flex justify-content-between align-items-center mb-4">
                <h4 className="text-primary mb-0">Cadena de Valor</h4>
                <button className="btn btn-outline-primary btn-sm" onClick={fetchData}>
                    <RefreshCw size={14} className="me-1" /> Recargar Datos
                </button>
            </div>

            {objectives.map((obj) => (
                <div key={obj.id} className="card mb-5 border-primary shadow-sm">
                    <div className="card-header bg-primary text-white d-flex justify-content-between align-items-center">
                        <h5 className="mb-0">Objetivo: {obj.name}</h5>
                        <button className="btn btn-light btn-sm fw-bold" onClick={() => handleAddProduct(obj.id)}>
                            <Plus size={16} /> Nuevo Producto
                        </button>
                    </div>

                    <div className="card-body bg-light">
                        {obj.products.map((prod) => (
                            <div key={prod.id} className="row mb-4 bg-white rounded border p-3 shadow-sm mx-1 position-relative">

                                {/* LADO IZQUIERDO: PRODUCTO */}
                                <div className="col-md-5 border-end">
                                    <div className="d-flex justify-content-between border-bottom mb-3 pb-2">
                                        <h6 className="text-success fw-bold mb-0">📦 Datos del Producto</h6>
                                        <button className="btn btn-outline-danger btn-sm border-0" onClick={() => handleDeleteProduct(prod.id)}>
                                            <Trash2 size={14} />
                                        </button>
                                    </div>
                                    <div className="row g-3">
                                        <div className="col-12">
                                            <label className="small fw-bold text-muted">Medido a través de:</label>
                                            <input
                                                type="text" className="form-control form-control-sm"
                                                value={prod.measured_through || ""}
                                                onChange={(e) => handleProductChange(obj.id, prod.id, 'measured_through', e.target.value)}
                                            />
                                        </div>
                                        <div className="col-6">
                                            <label className="small fw-bold text-muted">Cantidad:</label>
                                            <input
                                                type="number" className="form-control form-control-sm"
                                                value={prod.quantity || 0}
                                                onChange={(e) => handleProductChange(obj.id, prod.id, 'quantity', e.target.value)}
                                            />
                                        </div>
                                        <div className="col-6">
                                            <label className="small fw-bold text-muted">Costo Unitario:</label>
                                            <input
                                                type="number" className="form-control form-control-sm"
                                                value={prod.cost || 0}
                                                onChange={(e) => handleProductChange(obj.id, prod.id, 'cost', e.target.value)}
                                            />
                                        </div>
                                        <div className="col-12">
                                            <label className="small fw-bold text-muted">Etapa:</label>
                                            <select
                                                className="form-select form-select-sm"
                                                value={prod.stage || "Planeación"}
                                                onChange={(e) => handleProductChange(obj.id, prod.id, 'stage', e.target.value)}
                                            >
                                                <option value="Planeación">Planeación</option>
                                                <option value="Ejecución">Ejecución</option>
                                                <option value="Finalizado">Finalizado</option>
                                            </select>
                                        </div>
                                    </div>
                                </div>

                                {/* LADO DERECHO: ACTIVIDADES */}
                                <div className="col-md-7">
                                    <div className="d-flex justify-content-between align-items-center mb-3">
                                        <h6 className="text-secondary fw-bold mb-0 ps-2">🛠️ Actividades</h6>
                                        <button className="btn btn-outline-secondary btn-sm" onClick={() => handleAddActivity(prod.id)}>
                                            <Plus size={14} /> Añadir Actividad
                                        </button>
                                    </div>

                                    <div className="table-responsive">
                                        <table className="table table-sm table-hover border mb-0">
                                            <thead className="table-secondary">
                                                <tr>
                                                    <th>Costo de Actividad</th>
                                                    <th>Etapa</th>
                                                    <th style={{ width: "40px" }}></th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {prod.activities.map((act) => (
                                                    <tr key={act.id}>
                                                        <td>
                                                            <div className="input-group input-group-sm">
                                                                <span className="input-group-text border-0 bg-transparent">$</span>
                                                                <input
                                                                    type="number" className="form-control form-control-sm border-0 bg-transparent"
                                                                    value={act.cost || 0}
                                                                    onChange={(e) => handleActivityChange(obj.id, prod.id, act.id, 'cost', e.target.value)}
                                                                />
                                                            </div>
                                                        </td>
                                                        <td>
                                                            <select
                                                                className="form-select form-select-sm border-0 bg-transparent shadow-none"
                                                                value={act.stage || "Ejecución"}
                                                                onChange={(e) => handleActivityChange(obj.id, prod.id, act.id, 'stage', e.target.value)}
                                                            >
                                                                <option value="Planeación">Planeación</option>
                                                                <option value="Ejecución">Ejecución</option>
                                                            </select>
                                                        </td>
                                                        <td className="align-middle">
                                                            <button className="btn btn-link btn-sm text-danger p-0 shadow-none" onClick={() => handleDeleteActivity(act.id)}>
                                                                <Trash2 size={14} />
                                                            </button>
                                                        </td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>

                                    {/* BOTÓN GUARDAR (Para este producto y sus actividades) */}
                                    <div className="mt-3 text-end">
                                        <button
                                            className="btn btn-success btn-sm px-4 fw-bold shadow-sm"
                                            onClick={() => handleSaveEverything(obj.id, prod)}
                                            disabled={savingId === prod.id}
                                        >
                                            {savingId === prod.id ? (
                                                <> <RefreshCw size={14} className="spinner-border spinner-border-sm me-2" /> Guardando... </>
                                            ) : (
                                                <> <Save size={14} className="me-2" /> Guardar Producto y Actividades </>
                                            )}
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