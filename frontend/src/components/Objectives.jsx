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
                await api.put(`/objectives/${objectiveId}`, payload);
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
                        ? `/objectives-causes/${id}`
                        : `/objectives-indicators/${id}`;

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

    return (
        <div className="container mt-4">
            {/* General Objective */}
            <div className="mb-4">
                <h2>Objetivo General</h2>
                <textarea
                    className="form-control mb-3"
                    value={generalObjective}
                    onChange={(e) => setGeneralObjective(e.target.value)}
                    placeholder="Describe el objetivo general"
                />
                <textarea
                    className="form-control mb-3"
                    value={generalProblem}
                    onChange={(e) => setGeneralProblem(e.target.value)}
                    placeholder="Describe la relación con las causas"
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
                                        <td>{c.type}</td>
                                        <td>{c.cause_related}</td>
                                        <td>{c.specifics_objectives}</td>
                                        <td>
                                            <button
                                                className="btn btn-sm btn-primary me-2"
                                                onClick={() =>
                                                    navigate(
                                                        `/projects/${projectId}/edit-objective-cause/${c.id}`
                                                    )
                                                }
                                            >
                                                Editar
                                            </button>
                                            <button
                                                className="btn btn-sm btn-danger"
                                                onClick={() => handleDelete(c.id, "cause")}
                                            >
                                                Eliminar
                                            </button>
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
                                        <td>{i.indicator}</td>
                                        <td>{i.unit}</td>
                                        <td>{i.meta}</td>
                                        <td>{i.source_type}</td>
                                        <td>{i.source_validation}</td>
                                        <td>
                                            <button
                                                className="btn btn-sm btn-primary me-2"
                                                onClick={() =>
                                                    navigate(
                                                        `/projects/${projectId}/edit-objective-indicator/${i.id}`
                                                    )
                                                }
                                            >
                                                Editar
                                            </button>
                                            <button
                                                className="btn btn-sm btn-danger"
                                                onClick={() => handleDelete(i.id, "indicator")}
                                            >
                                                Eliminar
                                            </button>
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
