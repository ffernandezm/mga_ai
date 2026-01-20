import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";
import ObjectivesOptions from "../data/ObjectivesOptions";

function Objectives({ projectId }) {
    const [objectives, setObjectives] = useState([]);
    const [objectivesCauses, setObjectivesCauses] = useState([]);
    const [objectivesIndicators, setObjectivesIndicators] = useState([]);
    const [generalObjective, setGeneralObjective] = useState("");
    const [generalProblem, setGeneralProblem] = useState("");
    const [objectiveId, setObjectiveId] = useState(null);

    // ---------- EDICIÓN ----------
    const [editingCauseId, setEditingCauseId] = useState(null);
    const [editingIndicatorId, setEditingIndicatorId] = useState(null);
    const [editedCause, setEditedCause] = useState({});
    const [editedIndicator, setEditedIndicator] = useState({});

    // ---------- CREACIÓN INLINE ----------
    const [creatingCause, setCreatingCause] = useState(false);
    const [creatingIndicator, setCreatingIndicator] = useState(false);

    const [newCause, setNewCause] = useState({
        type: "",
        cause_related: "",
        specifics_objectives: "",
    });

    const [newIndicator, setNewIndicator] = useState({
        indicator: "",
        unit: "",
        meta: 0,
        source_type: "",
        source_validation: "",
    });

    const navigate = useNavigate();

    const fetchObjectives = async () => {
        try {
            const res = await api.get(`/objectives/${projectId}`);
            const data = res.data;

            if (data && data.length > 0) {
                const obj = data[0];
                setObjectives(data);
                setObjectiveId(obj.id);
                setGeneralObjective(obj.general_objective || "");
                setGeneralProblem(obj.general_problem || "");
                setObjectivesCauses(obj.objectives_causes || []);
                setObjectivesIndicators(obj.objectives_indicators || []);
            }
        } catch (error) {
            console.error("Error al obtener objetivos:", error);
        }
    };

    useEffect(() => {
        if (projectId) fetchObjectives();
    }, [projectId]);

    const handleSubmit = async () => {
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
            alert("Objetivo guardado correctamente.");
            fetchObjectives();
        } catch (err) {
            console.error(err);
            alert("Error al guardar.");
        }
    };

    const handleDelete = async (id, type) => {
        if (!window.confirm("¿Eliminar este registro?")) return;

        const endpoint =
            type === "cause"
                ? `/objectives_causes/${id}`
                : `/objectives_indicator/${id}`;

        await api.delete(endpoint);

        if (type === "cause") {
            setObjectivesCauses(prev => prev.filter(c => c.id !== id));
        } else {
            setObjectivesIndicators(prev => prev.filter(i => i.id !== id));
        }
    };

    // ---------- EDICIÓN ----------
    const handleEditCause = (c) => {
        setEditingCauseId(c.id);
        setEditedCause({ ...c });
    };

    const handleEditIndicator = (i) => {
        setEditingIndicatorId(i.id);
        setEditedIndicator({ ...i });
    };

    const handleSaveCause = async () => {
        await api.put(`/objectives_causes/${editingCauseId}`, editedCause);
        setObjectivesCauses(prev =>
            prev.map(c => (c.id === editingCauseId ? editedCause : c))
        );
        setEditingCauseId(null);
    };

    const handleSaveIndicator = async () => {
        await api.put(`/objectives_indicator/${editingIndicatorId}`, editedIndicator);
        setObjectivesIndicators(prev =>
            prev.map(i => (i.id === editingIndicatorId ? editedIndicator : i))
        );
        setEditingIndicatorId(null);
    };

    const handleCancelEdit = () => {
        setEditingCauseId(null);
        setEditingIndicatorId(null);
        setEditedCause({});
        setEditedIndicator({});
    };

    // ---------- CREACIÓN INLINE ----------
    const saveNewCause = async () => {
        const payload = { ...newCause, objective_id: objectiveId };
        const res = await api.post("/objectives_causes/", payload);
        setObjectivesCauses(prev => [...prev, res.data]);
        setCreatingCause(false);
        setNewCause({ type: "", cause_related: "", specifics_objectives: "" });
    };

    const saveNewIndicator = async () => {
        const payload = { ...newIndicator, objective_id: objectiveId };
        const res = await api.post("/objectives_indicator/", payload);
        setObjectivesIndicators(prev => [...prev, res.data]);
        setCreatingIndicator(false);
        setNewIndicator({
            indicator: "",
            unit: "",
            meta: 0,
            source_type: "",
            source_validation: "",
        });
    };

    return (
        <div className="container mt-4">
            {/* ---------- GENERAL ---------- */}
            <h2>Problema Central</h2>
            <textarea
                className="form-control mb-3"
                value={generalProblem}
                onChange={e => setGeneralProblem(e.target.value)}
            />

            <h2>Objetivo General</h2>
            <textarea
                className="form-control mb-4"
                value={generalObjective}
                onChange={e => setGeneralObjective(e.target.value)}
            />

            {/* ---------- CAUSAS ---------- */}
            <h2>Relación con Causas</h2>
            <table className="table table-bordered">
                <thead className="table-dark">
                    <tr>
                        <th>ID</th>
                        <th>Tipo</th>
                        <th>Causa</th>
                        <th>Objetivo Específico</th>
                        <th>Acciones</th>
                    </tr>
                </thead>
                <tbody>
                    {objectivesCauses.map(c => (
                        <tr key={c.id}>
                            <td>{c.id}</td>
                            <td>
                                {editingCauseId === c.id ? (
                                    <input
                                        className="form-control form-control-sm"
                                        value={editedCause.type || ""}
                                        onChange={e => setEditedCause({ ...editedCause, type: e.target.value })}
                                    />
                                ) : c.type}
                            </td>
                            <td>
                                {editingCauseId === c.id ? (
                                    <input
                                        className="form-control form-control-sm"
                                        value={editedCause.cause_related || ""}
                                        onChange={e => setEditedCause({ ...editedCause, cause_related: e.target.value })}
                                    />
                                ) : c.cause_related}
                            </td>
                            <td>
                                {editingCauseId === c.id ? (
                                    <textarea
                                        className="form-control form-control-sm"
                                        value={editedCause.specifics_objectives || ""}
                                        onChange={e => setEditedCause({ ...editedCause, specifics_objectives: e.target.value })}
                                    />
                                ) : c.specifics_objectives}
                            </td>
                            <td>
                                {editingCauseId === c.id ? (
                                    <>
                                        <button className="btn btn-sm btn-success me-2" onClick={handleSaveCause}>Guardar</button>
                                        <button className="btn btn-sm btn-secondary" onClick={handleCancelEdit}>Cancelar</button>
                                    </>
                                ) : (
                                    <>
                                        <button className="btn btn-sm btn-primary me-2" onClick={() => handleEditCause(c)}>Editar</button>
                                        <button className="btn btn-sm btn-danger" onClick={() => handleDelete(c.id, "cause")}>Eliminar</button>
                                    </>
                                )}
                            </td>
                        </tr>
                    ))}

                    {creatingCause && (
                        <tr>
                            <td>Nuevo</td>
                            <td>
                                <input className="form-control form-control-sm"
                                    value={newCause.type}
                                    onChange={e => setNewCause({ ...newCause, type: e.target.value })} />
                            </td>
                            <td>
                                <input className="form-control form-control-sm"
                                    value={newCause.cause_related}
                                    onChange={e => setNewCause({ ...newCause, cause_related: e.target.value })} />
                            </td>
                            <td>
                                <textarea className="form-control form-control-sm"
                                    value={newCause.specifics_objectives}
                                    onChange={e => setNewCause({ ...newCause, specifics_objectives: e.target.value })} />
                            </td>
                            <td>
                                <button className="btn btn-sm btn-success me-2" onClick={saveNewCause}>Guardar</button>
                                <button className="btn btn-sm btn-secondary" onClick={() => setCreatingCause(false)}>Cancelar</button>
                            </td>
                        </tr>
                    )}
                </tbody>
            </table>

            <button className="btn btn-success mb-4" onClick={() => setCreatingCause(true)} disabled={creatingCause}>
                Crear Causa
            </button>

            {/* ---------- INDICADORES ---------- */}
            <h2>Indicadores</h2>
            <table className="table table-bordered">
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
                    {objectivesIndicators.map(i => (
                        <tr key={i.id}>
                            <td>{i.id}</td>

                            <td>
                                {editingIndicatorId === i.id ? (
                                    <input
                                        className="form-control form-control-sm"
                                        value={editedIndicator.indicator || ""}
                                        onChange={e => setEditedIndicator({ ...editedIndicator, indicator: e.target.value })}
                                    />
                                ) : i.indicator}
                            </td>

                            <td>
                                {editingIndicatorId === i.id ? (
                                    <select
                                        className="form-control form-control-sm"
                                        value={editedIndicator.unit || ""}
                                        onChange={e => setEditedIndicator({ ...editedIndicator, unit: e.target.value })}
                                    >
                                        <option value="">Seleccione unidad</option>
                                        {ObjectivesOptions.Unit.map(u => (
                                            <option key={u} value={u}>{u}</option>
                                        ))}
                                    </select>
                                ) : i.unit}
                            </td>

                            <td>
                                {editingIndicatorId === i.id ? (
                                    <input
                                        type="number"
                                        className="form-control form-control-sm"
                                        value={editedIndicator.meta || 0}
                                        onChange={e =>
                                            setEditedIndicator({
                                                ...editedIndicator,
                                                meta: parseFloat(e.target.value) || 0
                                            })
                                        }
                                    />
                                ) : i.meta}
                            </td>

                            <td>
                                {editingIndicatorId === i.id ? (
                                    <select
                                        className="form-control form-control-sm"
                                        value={editedIndicator.source_type || ""}
                                        onChange={e => setEditedIndicator({ ...editedIndicator, source_type: e.target.value })}
                                    >
                                        <option value="">Seleccione fuente</option>
                                        {ObjectivesOptions.Source_type.map(s => (
                                            <option key={s} value={s}>{s}</option>
                                        ))}
                                    </select>
                                ) : i.source_type}
                            </td>

                            <td>
                                {editingIndicatorId === i.id ? (
                                    <input
                                        className="form-control form-control-sm"
                                        value={editedIndicator.source_validation || ""}
                                        onChange={e => setEditedIndicator({ ...editedIndicator, source_validation: e.target.value })}
                                    />
                                ) : i.source_validation}
                            </td>

                            <td>
                                {editingIndicatorId === i.id ? (
                                    <>
                                        <button className="btn btn-sm btn-success me-2" onClick={handleSaveIndicator}>Guardar</button>
                                        <button className="btn btn-sm btn-secondary" onClick={handleCancelEdit}>Cancelar</button>
                                    </>
                                ) : (
                                    <>
                                        <button className="btn btn-sm btn-primary me-2" onClick={() => handleEditIndicator(i)}>Editar</button>
                                        <button className="btn btn-sm btn-danger" onClick={() => handleDelete(i.id, "indicator")}>Eliminar</button>
                                    </>
                                )}
                            </td>
                        </tr>
                    ))}

                    {creatingIndicator && (
                        <tr>
                            <td>Nuevo</td>
                            <td>
                                <input className="form-control form-control-sm"
                                    value={newIndicator.indicator}
                                    onChange={e => setNewIndicator({ ...newIndicator, indicator: e.target.value })} />
                            </td>
                            <td>
                                <select className="form-control form-control-sm"
                                    value={newIndicator.unit}
                                    onChange={e => setNewIndicator({ ...newIndicator, unit: e.target.value })}>
                                    <option value="">Seleccione unidad</option>
                                    {ObjectivesOptions.Unit.map(u => (
                                        <option key={u} value={u}>{u}</option>
                                    ))}
                                </select>
                            </td>
                            <td>
                                <input type="number" className="form-control form-control-sm"
                                    value={newIndicator.meta}
                                    onChange={e => setNewIndicator({ ...newIndicator, meta: parseFloat(e.target.value) || 0 })} />
                            </td>
                            <td>
                                <select className="form-control form-control-sm"
                                    value={newIndicator.source_type}
                                    onChange={e => setNewIndicator({ ...newIndicator, source_type: e.target.value })}>
                                    <option value="">Seleccione fuente</option>
                                    {ObjectivesOptions.Source_type.map(s => (
                                        <option key={s} value={s}>{s}</option>
                                    ))}
                                </select>
                            </td>
                            <td>
                                <input className="form-control form-control-sm"
                                    value={newIndicator.source_validation}
                                    onChange={e => setNewIndicator({ ...newIndicator, source_validation: e.target.value })} />
                            </td>
                            <td>
                                <button className="btn btn-sm btn-success me-2" onClick={saveNewIndicator}>Guardar</button>
                                <button className="btn btn-sm btn-secondary" onClick={() => setCreatingIndicator(false)}>Cancelar</button>
                            </td>
                        </tr>
                    )}
                </tbody>
            </table>

            <button
                className="btn btn-success mb-4"
                onClick={() => setCreatingIndicator(true)}
                disabled={creatingIndicator}
            >
                Crear Indicador
            </button>

            <div>
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
