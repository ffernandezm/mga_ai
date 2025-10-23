import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../services/api";

function Objectives({ projectId }) {
    const [objectives, setObjectives] = useState([]);
    const [objectivesCauses, setObjectivesCauses] = useState([]);
    const [objectivesIndicators, setObjectivesIndicators] = useState([]);
    const [generalObjective, setGeneralObjective] = useState("");
    const [generalProblem, setGeneralProblem] = useState("");
    const [objectiveId, setObjectiveId] = useState(null);

    // Estados para edición en línea - NUEVOS ESTADOS
    const [editingCauseId, setEditingCauseId] = useState(null);
    const [editingIndicatorId, setEditingIndicatorId] = useState(null);
    const [editedCause, setEditedCause] = useState({});
    const [editedIndicator, setEditedIndicator] = useState({});

    const navigate = useNavigate();

    const fetchObjectives = async () => {
        try {
            const response = await api.get(`/objectives/${projectId}`);
            const data = response.data;

            if (data) {
                setObjectives(data);
                if (data.length > 0) {
                    const firstObjective = data[0];
                    setObjectiveId(firstObjective.id);
                    setGeneralObjective(firstObjective.general_objective || "");
                    setGeneralProblem(firstObjective.general_problem || "");
                    setObjectivesCauses(firstObjective.objectives_causes || []);
                    setObjectivesIndicators(firstObjective.objectives_indicators || []);
                }
            }
        } catch (error) {
            console.error("Error al obtener los objetivos:", error);
        }
    };

    useEffect(() => {
        if (projectId) fetchObjectives();
    }, [projectId]);

    const handleSubmit = async () => {
        if (!projectId) return alert("No hay proyecto seleccionado.");

        const payload = {
            project_id: projectId,
            general_objective: generalObjective,
            general_problem: generalProblem,
            objectives_causes: objectivesCauses,
            objectives_indicators: objectivesIndicators,
        };

        try {
            if (objectiveId) {
                await api.put(`/objectives/${projectId}/${objectiveId}`, payload);
            } else {
                const res = await api.post(`/objectives`, payload);
                setObjectiveId(res.data.id);
            }
            alert("Objetivo actualizado correctamente.");
            fetchObjectives();
        } catch (err) {
            console.error("Error al guardar el objetivo:", err);
            alert("Error al guardar el objetivo.");
        }
    };

    const handleDelete = async (id, type) => {
        if (!id) return;
        if (window.confirm("¿Eliminar este registro?")) {
            try {
                const endpoint =
                    type === "cause"
                        ? `/objectives_causes/${id}`
                        : `/objectives_indicator/${id}`;

                await api.delete(endpoint);

                if (type === "cause") {
                    setObjectivesCauses(prev => prev.filter(item => item.id !== id));
                } else {
                    setObjectivesIndicators(prev => prev.filter(item => item.id !== id));
                }
            } catch (error) {
                console.error("Error al eliminar registro:", error);
                alert("Error al eliminar registro.");
            }
        }
    };

    // FUNCIONES NUEVAS PARA EDICIÓN EN LÍNEA

    const handleEditCause = (cause) => {
        setEditingCauseId(cause.id);
        setEditedCause({ ...cause });
    };

    const handleEditIndicator = (indicator) => {
        setEditingIndicatorId(indicator.id);
        setEditedIndicator({ ...indicator });
    };

    const handleSaveCause = async () => {
        try {
            await api.put(`/objectives_causes/${editingCauseId}`, editedCause);

            setObjectivesCauses(prev =>
                prev.map(cause =>
                    cause.id === editingCauseId ? { ...editedCause } : cause
                )
            );

            setEditingCauseId(null);
            setEditedCause({});
            alert("Causa actualizada correctamente.");
        } catch (error) {
            console.error("Error al actualizar causa:", error);
            alert("Error al actualizar causa.");
        }
    };

    const handleSaveIndicator = async () => {
        try {
            await api.put(`/objectives_indicator/${editingIndicatorId}`, editedIndicator);

            setObjectivesIndicators(prev =>
                prev.map(indicator =>
                    indicator.id === editingIndicatorId ? { ...editedIndicator } : indicator
                )
            );

            setEditingIndicatorId(null);
            setEditedIndicator({});
            alert("Indicador actualizado correctamente.");
        } catch (error) {
            console.error("Error al actualizar indicador:", error);
            alert("Error al actualizar indicador.");
        }
    };

    const handleCancelEdit = () => {
        setEditingCauseId(null);
        setEditingIndicatorId(null);
        setEditedCause({});
        setEditedIndicator({});
    };

    const handleCauseChange = (field, value) => {
        setEditedCause(prev => ({
            ...prev,
            [field]: value
        }));
    };

    const handleIndicatorChange = (field, value) => {
        setEditedIndicator(prev => ({
            ...prev,
            [field]: field === 'meta' ? parseFloat(value) || 0 : value
        }));
    };

    return (
        <div className="container mt-4">
            {/* General Objective */}
            <div className="mb-4">
                <h2>Problema Central</h2>
                <textarea
                    className="form-control mb-3"
                    value={generalProblem}
                    onChange={(e) => setGeneralProblem(e.target.value)}
                    placeholder="Describe el problema general"
                />
                <h2>Objetivo general - Propósito*</h2>
                <textarea
                    className="form-control mb-3"
                    value={generalObjective}
                    onChange={(e) => setGeneralObjective(e.target.value)}
                    placeholder="Describe el objetivo general"
                />
            </div>

            {/* Objectives Causes */}
            <div className="mb-5">
                <h2>Relación con Causas</h2>
                <Link
                    to={`/projects/${projectId}/create-objective-cause/${objectiveId}`}
                    className="btn btn-success mb-3"
                >
                    Crear Registro de Causa
                </Link>
                <div className="table-responsive">
                    <table className="table table-striped table-bordered">
                        <thead className="table-dark">
                            <tr>
                                <th>ID</th>
                                <th>Tipo</th>
                                <th>Causa Relacionada</th>
                                <th>Objetivo Específico</th>
                                <th>Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            {objectivesCauses.length > 0 ? (
                                objectivesCauses.map((c) => (
                                    <tr key={c.id}>
                                        <td>{c.id}</td>
                                        <td>
                                            {editingCauseId === c.id ? (
                                                <select
                                                    className="form-control form-control-sm"
                                                    value={editedCause.type || ''}
                                                    onChange={(e) => handleCauseChange('type', e.target.value)}
                                                >
                                                    <option value="">Seleccionar tipo</option>
                                                    <option value="Estratégico">Estratégico</option>
                                                    <option value="Operativo">Operativo</option>
                                                    <option value="Táctico">Táctico</option>
                                                </select>
                                            ) : (
                                                c.type
                                            )}
                                        </td>
                                        <td>
                                            {editingCauseId === c.id ? (
                                                <input
                                                    type="text"
                                                    className="form-control form-control-sm"
                                                    value={editedCause.cause_related || ''}
                                                    onChange={(e) => handleCauseChange('cause_related', e.target.value)}
                                                />
                                            ) : (
                                                c.cause_related
                                            )}
                                        </td>
                                        <td>
                                            {editingCauseId === c.id ? (
                                                <textarea
                                                    className="form-control form-control-sm"
                                                    value={editedCause.specifics_objectives || ''}
                                                    onChange={(e) => handleCauseChange('specifics_objectives', e.target.value)}
                                                    rows="2"
                                                />
                                            ) : (
                                                c.specifics_objectives
                                            )}
                                        </td>
                                        <td>
                                            {editingCauseId === c.id ? (
                                                <div>
                                                    <button
                                                        className="btn btn-sm btn-success me-2"
                                                        onClick={handleSaveCause}
                                                    >
                                                        Guardar
                                                    </button>
                                                    <button
                                                        className="btn btn-sm btn-secondary"
                                                        onClick={handleCancelEdit}
                                                    >
                                                        Cancelar
                                                    </button>
                                                </div>
                                            ) : (
                                                <div>
                                                    <button
                                                        className="btn btn-sm btn-primary me-2"
                                                        onClick={() => handleEditCause(c)}
                                                    >
                                                        Editar
                                                    </button>
                                                    <button
                                                        className="btn btn-sm btn-danger"
                                                        onClick={() => handleDelete(c.id, "cause")}
                                                    >
                                                        Eliminar
                                                    </button>
                                                </div>
                                            )}
                                        </td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan="5" className="text-center">
                                        No hay registros de causas.
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Objectives Indicators */}
            <div className="mb-5">
                <h2>Indicadores</h2>
                <Link
                    to={`/projects/${projectId}/create-objective-indicator/${objectiveId}`}
                    className="btn btn-success mb-3"
                >
                    Crear Indicador
                </Link>
                <div className="table-responsive">
                    <table className="table table-striped table-bordered">
                        <thead className="table-dark">
                            <tr>
                                <th>ID</th>
                                <th>Indicador</th>
                                <th>Unidad</th>
                                <th>Meta</th>
                                <th>Fuente</th>
                                <th>Validación</th>
                                <th>Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            {objectivesIndicators.length > 0 ? (
                                objectivesIndicators.map((i) => (
                                    <tr key={i.id}>
                                        <td>{i.id}</td>
                                        <td>
                                            {editingIndicatorId === i.id ? (
                                                <input
                                                    type="text"
                                                    className="form-control form-control-sm"
                                                    value={editedIndicator.indicator || ''}
                                                    onChange={(e) => handleIndicatorChange('indicator', e.target.value)}
                                                />
                                            ) : (
                                                i.indicator
                                            )}
                                        </td>
                                        <td>
                                            {editingIndicatorId === i.id ? (
                                                <input
                                                    type="text"
                                                    className="form-control form-control-sm"
                                                    value={editedIndicator.unit || ''}
                                                    onChange={(e) => handleIndicatorChange('unit', e.target.value)}
                                                />
                                            ) : (
                                                i.unit
                                            )}
                                        </td>
                                        <td>
                                            {editingIndicatorId === i.id ? (
                                                <input
                                                    type="number"
                                                    step="0.01"
                                                    className="form-control form-control-sm"
                                                    value={editedIndicator.meta || 0}
                                                    onChange={(e) => handleIndicatorChange('meta', e.target.value)}
                                                />
                                            ) : (
                                                i.meta
                                            )}
                                        </td>
                                        <td>
                                            {editingIndicatorId === i.id ? (
                                                <input
                                                    type="text"
                                                    className="form-control form-control-sm"
                                                    value={editedIndicator.source_type || ''}
                                                    onChange={(e) => handleIndicatorChange('source_type', e.target.value)}
                                                />
                                            ) : (
                                                i.source_type
                                            )}
                                        </td>
                                        <td>
                                            {editingIndicatorId === i.id ? (
                                                <input
                                                    type="text"
                                                    className="form-control form-control-sm"
                                                    value={editedIndicator.source_validation || ''}
                                                    onChange={(e) => handleIndicatorChange('source_validation', e.target.value)}
                                                />
                                            ) : (
                                                i.source_validation
                                            )}
                                        </td>
                                        <td>
                                            {editingIndicatorId === i.id ? (
                                                <div>
                                                    <button
                                                        className="btn btn-sm btn-success me-2"
                                                        onClick={handleSaveIndicator}
                                                    >
                                                        Guardar
                                                    </button>
                                                    <button
                                                        className="btn btn-sm btn-secondary"
                                                        onClick={handleCancelEdit}
                                                    >
                                                        Cancelar
                                                    </button>
                                                </div>
                                            ) : (
                                                <div>
                                                    <button
                                                        className="btn btn-sm btn-primary me-2"
                                                        onClick={() => handleEditIndicator(i)}
                                                    >
                                                        Editar
                                                    </button>
                                                    <button
                                                        className="btn btn-sm btn-danger"
                                                        onClick={() => handleDelete(i.id, "indicator")}
                                                    >
                                                        Eliminar
                                                    </button>
                                                </div>
                                            )}
                                        </td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan="7" className="text-center">
                                        No hay registros de indicadores.
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            <div className="mt-4">
                <button className="btn btn-secondary me-2" onClick={() => navigate("/projects")}>
                    Regresar
                </button>
                <button className="btn btn-primary" onClick={handleSubmit}>
                    Guardar Cambios
                </button>
            </div>
        </div>
    );
}

export default Objectives;