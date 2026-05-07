import { useState, useMemo, useEffect, useCallback } from "react";
import api from "../services/api";
import "../styles/ProductCatalogWizard.css";

const PAGE_SIZE = 10;

const emptyFilters = {
    plan_name: "",
    pillar_description: "",
    objective_description: "",
    strategy_description: "",
    component_description: "",
};

function PndDetailWizard({ isOpen, onClose, onSelect }) {
    const [filters, setFilters] = useState(emptyFilters);
    const [currentPage, setCurrentPage] = useState(1);
    const [selectedRow, setSelectedRow] = useState(null);

    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const fetchData = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await api.get("/pnd_details/");
            setData(response.data);
        } catch (err) {
            console.error("Error cargando detalle PND:", err);
            setError("No se pudo cargar el detalle PND. Intente nuevamente.");
            setData([]);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        if (isOpen) {
            fetchData();
        }
    }, [isOpen, fetchData]);

    const filteredRows = useMemo(() => {
        let rows = data;

        // if (filters.plan_name) {
        //     rows = rows.filter(r =>
        //         (r.plan_name || "").toLowerCase().includes(filters.plan_name.toLowerCase())
        //     );
        // }
        if (filters.pillar_description) {
            rows = rows.filter(r =>
                (r.pillar_description || "").toLowerCase().includes(filters.pillar_description.toLowerCase())
            );
        }
        if (filters.objective_description) {
            rows = rows.filter(r =>
                (r.objective_description || "").toLowerCase().includes(filters.objective_description.toLowerCase())
            );
        }
        if (filters.strategy_description) {
            rows = rows.filter(r =>
                (r.strategy_description || "").toLowerCase().includes(filters.strategy_description.toLowerCase())
            );
        }
        if (filters.component_description) {
            rows = rows.filter(r =>
                (r.component_description || "").toLowerCase().includes(filters.component_description.toLowerCase())
            );
        }

        return rows;
    }, [data, filters]);

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
        setSelectedRow(prev => prev?.id === row.id ? null : row);
    };

    const handleAccept = () => {
        if (!selectedRow || !onSelect) return;
        onSelect({
            transformation: selectedRow.pillar_description || "",
            pillar: selectedRow.objective_description || "",
            catalyst: selectedRow.strategy_description || "",
            component: selectedRow.component_description || "",
        });
        handleClose();
    };

    const handleClose = () => {
        setFilters(emptyFilters);
        setCurrentPage(1);
        setSelectedRow(null);
        onClose();
    };

    if (!isOpen) return null;

    return (
        <div className="wizard-overlay" onClick={handleClose}>
            <div className="wizard-modal" style={{ maxWidth: "1100px" }} onClick={e => e.stopPropagation()}>
                <div className="wizard-header">
                    <h3>Detalle Plan Nacional de Desarrollo</h3>
                    <button className="wizard-close-btn" onClick={handleClose}>&times;</button>
                </div>

                <div className="wizard-body">
                    {error && <div className="wizard-error">{error}</div>}

                    <div className="wizard-table-container">
                        <table className="wizard-table">
                            <thead>
                                <tr>
                                    {/* <th>Plan</th> */}
                                    <th>Pilar / Transformación</th>
                                    <th>Objetivo</th>
                                    <th>Estrategia / Catalizador</th>
                                    <th>Componente</th>
                                </tr>
                                <tr className="wizard-filter-row">
                                    {/* <th>
                                        <input
                                            type="text"
                                            placeholder="Buscar..."
                                            value={filters.plan_name}
                                            onChange={e => handleFilterChange("plan_name", e.target.value)}
                                        />
                                    </th> */}
                                    <th>
                                        <input
                                            type="text"
                                            placeholder="Buscar..."
                                            value={filters.pillar_description}
                                            onChange={e => handleFilterChange("pillar_description", e.target.value)}
                                        />
                                    </th>
                                    <th>
                                        <input
                                            type="text"
                                            placeholder="Buscar..."
                                            value={filters.objective_description}
                                            onChange={e => handleFilterChange("objective_description", e.target.value)}
                                        />
                                    </th>
                                    <th>
                                        <input
                                            type="text"
                                            placeholder="Buscar..."
                                            value={filters.strategy_description}
                                            onChange={e => handleFilterChange("strategy_description", e.target.value)}
                                        />
                                    </th>
                                    <th>
                                        <input
                                            type="text"
                                            placeholder="Buscar..."
                                            value={filters.component_description}
                                            onChange={e => handleFilterChange("component_description", e.target.value)}
                                        />
                                    </th>
                                </tr>
                            </thead>
                            <tbody>
                                {loading ? (
                                    <tr>
                                        <td colSpan={5} className="wizard-no-results">Cargando...</td>
                                    </tr>
                                ) : paginatedRows.length === 0 ? (
                                    <tr>
                                        <td colSpan={5} className="wizard-no-results">No se encontraron resultados.</td>
                                    </tr>
                                ) : (
                                    paginatedRows.map(row => (
                                        <tr
                                            key={row.id}
                                            onClick={() => handleRowClick(row)}
                                            className={`wizard-row-selectable${selectedRow?.id === row.id ? " wizard-row-selected" : ""}`}
                                        >
                                            {/* <td>{row.plan_name || "—"}</td> */}
                                            <td>{row.pillar_description}</td>
                                            <td>{row.objective_description}</td>
                                            <td>{row.strategy_description}</td>
                                            <td>{row.component_description}</td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>

                    {/* Paginación */}
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
                </div>

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

export default PndDetailWizard;
