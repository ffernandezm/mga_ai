import { useState, useMemo, useEffect, useCallback } from "react";
import api from "../services/api";
import "../styles/ProductCatalogWizard.css";

const PAGE_SIZE = 10;

const emptyFilters = {
    nombre: "",
    descripcion: "",
    unidadMedida: "",
    codigoPrograma: "",
    producto: "",
};

function ProductCatalogWizard({ isOpen, onClose, onSelect }) {
    const [selectedSectorCode, setSelectedSectorCode] = useState("");
    const [filters, setFilters] = useState(emptyFilters);
    const [currentPage, setCurrentPage] = useState(1);
    const [selectedRow, setSelectedRow] = useState(null);

    const [catalogData, setCatalogData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const fetchCatalog = useCallback(async (sectorCode) => {
        setLoading(true);
        setError(null);
        try {
            const params = sectorCode ? { sector_code: sectorCode } : {};
            const response = await api.get("/product_catalogs/", { params });
            setCatalogData(response.data);
        } catch (err) {
            console.error("Error cargando catálogo de productos:", err);
            setError("No se pudo cargar el catálogo. Intente nuevamente.");
            setCatalogData([]);
        } finally {
            setLoading(false);
        }
    }, []);

    // Load all data on open to extract sector options
    useEffect(() => {
        if (isOpen) {
            fetchCatalog();
        }
    }, [isOpen, fetchCatalog]);

    const sectorOptions = useMemo(() => {
        const sectorMap = new Map();
        catalogData.forEach(item => {
            if (!sectorMap.has(item.sector_code)) {
                sectorMap.set(item.sector_code, item.sector_name);
            }
        });
        return [...sectorMap.entries()]
            .map(([code, name]) => ({ code, name }))
            .sort((a, b) => a.name.localeCompare(b.name, "es"));
    }, [catalogData]);

    const filteredRows = useMemo(() => {
        if (!selectedSectorCode) return [];

        let rows = catalogData.filter(
            item => String(item.sector_code) === String(selectedSectorCode)
        );

        if (filters.nombre) {
            rows = rows.filter(r =>
                r.product_name.toLowerCase().includes(filters.nombre.toLowerCase())
            );
        }
        if (filters.descripcion) {
            rows = rows.filter(r =>
                (r.description || "").toLowerCase().includes(filters.descripcion.toLowerCase())
            );
        }
        if (filters.unidadMedida) {
            rows = rows.filter(r =>
                (r.measurement_unit || "").toLowerCase().includes(filters.unidadMedida.toLowerCase())
            );
        }
        if (filters.codigoPrograma) {
            rows = rows.filter(r =>
                String(r.program_code).includes(filters.codigoPrograma)
            );
        }
        if (filters.producto) {
            const concat = (r) => `${r.product_code} - ${r.product_name}`;
            rows = rows.filter(r =>
                concat(r).toLowerCase().includes(filters.producto.toLowerCase())
            );
        }

        return rows;
    }, [catalogData, selectedSectorCode, filters]);

    const totalPages = Math.max(1, Math.ceil(filteredRows.length / PAGE_SIZE));

    const paginatedRows = useMemo(() => {
        const start = (currentPage - 1) * PAGE_SIZE;
        return filteredRows.slice(start, start + PAGE_SIZE);
    }, [filteredRows, currentPage]);

    const handleFilterChange = (field, value) => {
        setFilters(prev => ({ ...prev, [field]: value }));
        setCurrentPage(1);
        setSelectedRow(null);
    };

    const handleRowClick = (row) => {
        setSelectedRow(prev =>
            prev?.id === row.id ? null : row
        );
    };

    const handleAccept = () => {
        if (!selectedRow || !onSelect) return;
        onSelect({
            main_product: selectedRow.product_name,
            sector: selectedRow.sector_name,
            indicator_code: selectedRow.indicator_code,
        });
        handleClose();
    };

    const handleClose = () => {
        setSelectedSectorCode("");
        setFilters(emptyFilters);
        setCurrentPage(1);
        setSelectedRow(null);
        onClose();
    };

    if (!isOpen) return null;

    return (
        <div className="wizard-overlay" onClick={handleClose}>
            <div className="wizard-modal" onClick={e => e.stopPropagation()}>
                <div className="wizard-header">
                    <h3>Catálogo de Productos</h3>
                    <button className="wizard-close-btn" onClick={handleClose}>&times;</button>
                </div>

                <div className="wizard-body">
                    {error && <div className="wizard-error">{error}</div>}

                    <div className="wizard-sector-select">
                        <label>Seleccione un Sector</label>
                        {loading && catalogData.length === 0 ? (
                            <select disabled>
                                <option>Cargando sectores...</option>
                            </select>
                        ) : (
                            <select
                                value={selectedSectorCode}
                                onChange={e => {
                                    setSelectedSectorCode(e.target.value);
                                    setFilters(emptyFilters);
                                    setCurrentPage(1);
                                    setSelectedRow(null);
                                }}
                            >
                                <option value="">-- Seleccione --</option>
                                {sectorOptions.map(opt => (
                                    <option key={opt.code} value={opt.code}>
                                        {opt.name}
                                    </option>
                                ))}
                            </select>
                        )}
                    </div>

                    {selectedSectorCode && (
                        <>
                            <div className="wizard-table-container">
                                <table className="wizard-table">
                                    <thead>
                                        <tr>
                                            <th>Nombre</th>
                                            <th>Descripción</th>
                                            <th>Unidad de Medida</th>
                                            <th>Código Programa</th>
                                            <th>Producto</th>
                                        </tr>
                                        <tr className="wizard-filter-row">
                                            <th>
                                                <input
                                                    type="text"
                                                    placeholder="Buscar..."
                                                    value={filters.nombre}
                                                    onChange={e => handleFilterChange("nombre", e.target.value)}
                                                />
                                            </th>
                                            <th>
                                                <input
                                                    type="text"
                                                    placeholder="Buscar..."
                                                    value={filters.descripcion}
                                                    onChange={e => handleFilterChange("descripcion", e.target.value)}
                                                />
                                            </th>
                                            <th>
                                                <input
                                                    type="text"
                                                    placeholder="Buscar..."
                                                    value={filters.unidadMedida}
                                                    onChange={e => handleFilterChange("unidadMedida", e.target.value)}
                                                />
                                            </th>
                                            <th>
                                                <input
                                                    type="text"
                                                    placeholder="Buscar..."
                                                    value={filters.codigoPrograma}
                                                    onChange={e => handleFilterChange("codigoPrograma", e.target.value)}
                                                />
                                            </th>
                                            <th>
                                                <input
                                                    type="text"
                                                    placeholder="Buscar..."
                                                    value={filters.producto}
                                                    onChange={e => handleFilterChange("producto", e.target.value)}
                                                />
                                            </th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {loading ? (
                                            <tr>
                                                <td colSpan={5} className="wizard-no-results">
                                                    Cargando...
                                                </td>
                                            </tr>
                                        ) : paginatedRows.length === 0 ? (
                                            <tr>
                                                <td colSpan={5} className="wizard-no-results">
                                                    No se encontraron resultados.
                                                </td>
                                            </tr>
                                        ) : (
                                            paginatedRows.map((row) => (
                                                <tr
                                                    key={row.id}
                                                    onClick={() => handleRowClick(row)}
                                                    className={`wizard-row-selectable${selectedRow?.id === row.id
                                                            ? " wizard-row-selected"
                                                            : ""
                                                        }`}
                                                >
                                                    <td>{row.product_name}</td>
                                                    <td>{row.description}</td>
                                                    <td>{row.measurement_unit}</td>
                                                    <td>{row.program_code}</td>
                                                    <td>{row.product_code} - {row.product_name}</td>
                                                </tr>
                                            ))
                                        )}
                                    </tbody>
                                </table>
                            </div>

                            {/* Pagination */}
                            <div className="wizard-pagination">
                                <span className="wizard-pagination-info">
                                    Mostrando {filteredRows.length === 0 ? 0 : (currentPage - 1) * PAGE_SIZE + 1}
                                    –{Math.min(currentPage * PAGE_SIZE, filteredRows.length)} de {filteredRows.length}
                                </span>
                                <div className="wizard-pagination-controls">
                                    <button
                                        type="button"
                                        disabled={currentPage === 1}
                                        onClick={() => setCurrentPage(p => p - 1)}
                                    >
                                        Anterior
                                    </button>
                                    <span className="wizard-page-number">
                                        Página {currentPage} de {totalPages}
                                    </span>
                                    <button
                                        type="button"
                                        disabled={currentPage >= totalPages}
                                        onClick={() => setCurrentPage(p => p + 1)}
                                    >
                                        Siguiente
                                    </button>
                                </div>
                            </div>
                        </>
                    )}
                </div>

                {/* Footer con botones de acción */}
                <div className="wizard-footer">
                    <button type="button" className="wizard-btn-cancel" onClick={handleClose}>
                        Cancelar
                    </button>
                    <button
                        type="button"
                        className="wizard-btn-accept"
                        disabled={!selectedRow}
                        onClick={handleAccept}
                    >
                        Aceptar
                    </button>
                </div>
            </div>
        </div>
    );
}

export default ProductCatalogWizard;
