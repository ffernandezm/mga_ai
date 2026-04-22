import { useEffect, useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";
import { useNotification } from "../context/NotificationContext";
import participantesCsv from "../data/participantes.csv?raw";

function buildParticipantOptions(csv) {
    const lines = csv.split("\n").slice(1).filter((l) => l.trim());
    const actorSet = new Set();
    const entidad = {};

    for (const line of lines) {
        const [actor, entity] = line.split(";").map((s) => s.trim().replace(/^"|"$/g, ""));
        if (!actor) continue;
        actorSet.add(actor);
        if (!entity || entity === "Seleccione" || entity === "Departamento") continue;
        if (!entidad[actor]) entidad[actor] = [];
        entidad[actor].push(entity);
    }

    return {
        actor: [...actorSet].sort(),
        entidad,
        rol: ["A favor", "En contra", "Neutral", "No definida"],
    };
}

const participantOptions = buildParticipantOptions(participantesCsv);

const emptyParticipant = {
    participant_actor: "",
    participant_entity: "",
    interest_expectative: "",
    rol: "",
    contribution_conflicts: "",
};

function ParticipantsGeneral({ projectId }) {
    const { showSuccess, showError, showConfirmation } = useNotification();
    const [participantsGeneral, setParticipantsGeneral] = useState([]);
    const navigate = useNavigate();
    const [analysis, setAnalysis] = useState("");
    const [generalId, setGeneralId] = useState(null);

    // Estados de edición inline
    const [editingId, setEditingId] = useState(null);
    const [editedParticipant, setEditedParticipant] = useState({});

    // Estados de creación inline
    const [creating, setCreating] = useState(false);
    const [newParticipant, setNewParticipant] = useState({ ...emptyParticipant });

    const getEntityOptions = (actor) => participantOptions.entidad[actor] || [];
    const actorOptions = participantOptions.actor;
    const rolOptions = participantOptions.rol;

    const fetchParticipantsGeneral = async () => {
        try {
            const response = await api.get(`/participants_general/${projectId}`);
            const data = response.data;

            if (data.length > 0) {
                const general = data[0];
                setParticipantsGeneral(general.participants || []);
                setAnalysis(general.participants_analisis);
                setGeneralId(general.id);
            }
        } catch (error) {
            console.error("Error al obtener participantes:", error);
        }
    };

    useEffect(() => {
        if (projectId) fetchParticipantsGeneral();
    }, [projectId]);

    const handleSubmit = async () => {
        if (!projectId) return showError("No hay proyecto seleccionado.");
        const payload = {
            project_id: projectId,
            participants_analisis: analysis,
            participants: [],
        };

        try {
            if (generalId) {
                await api.put(`/participants_general/${generalId}`, payload);
            } else {
                const res = await api.post(`/participants_general`, payload);
                setGeneralId(res.data.id);
            }
            showSuccess("Participantes actualizados correctamente.");
            fetchParticipantsGeneral();
        } catch (err) {
            console.error("Error:", err);
            showError("Error al guardar la información.");
        }
    };

    const handleDeleteParticipant = async (participantId) => {
        if (!participantId) return;
        const confirmed = await showConfirmation({
            title: "Eliminar Participante",
            message: "¿Estás seguro de eliminar este participante?"
        });
        if (confirmed) {
            try {
                await api.delete(`/participants/${participantId}`);
                setParticipantsGeneral((prev) =>
                    prev.filter((p) => p.id !== participantId)
                );
                showSuccess("Participante eliminado correctamente.");
            } catch (error) {
                console.error("Error al eliminar participante:", error);
                showError("Error al eliminar el participante.");
            }
        }
    };

    // ---------- EDICIÓN INLINE ----------
    const handleEdit = (participant) => {
        setEditingId(participant.id);
        setEditedParticipant({ ...participant });
    };

    const handleEditChange = (field, value) => {
        setEditedParticipant((prev) => ({
            ...prev,
            [field]: value,
            ...(field === "participant_actor" && { participant_entity: "" }),
        }));
    };

    const handleSaveEdit = async () => {
        try {
            await api.put(`/participants/${editingId}`, editedParticipant);
            setParticipantsGeneral((prev) =>
                prev.map((p) => (p.id === editingId ? { ...editedParticipant } : p))
            );
            setEditingId(null);
            setEditedParticipant({});
            showSuccess("Participante actualizado correctamente.");
        } catch (error) {
            console.error("Error al actualizar participante:", error);
            showError("Error al actualizar el participante.");
        }
    };

    const handleCancelEdit = () => {
        setEditingId(null);
        setEditedParticipant({});
    };

    // ---------- CREACIÓN INLINE ----------
    const handleCreate = () => {
        setCreating(true);
        setNewParticipant({ ...emptyParticipant });
    };

    const handleNewChange = (field, value) => {
        setNewParticipant((prev) => ({
            ...prev,
            [field]: value,
            ...(field === "participant_actor" && { participant_entity: "" }),
        }));
    };

    const saveNewParticipant = async () => {
        try {
            const payload = { ...newParticipant, participants_general_id: generalId };
            const res = await api.post("/participants/", payload);
            setParticipantsGeneral((prev) => [...prev, res.data]);
            setCreating(false);
            setNewParticipant({ ...emptyParticipant });
            showSuccess("Participante creado correctamente.");
        } catch (error) {
            console.error("Error al crear participante:", error);
            showError("Hubo un error al crear el participante.");
        }
    };

    // Renderiza una celda de select o texto según esté en edición
    const renderSelectCell = (isEditing, value, onChange, options, placeholder) => (
        isEditing ? (
            <select
                className="form-control form-control-sm"
                value={value || ""}
                onChange={(e) => onChange(e.target.value)}
            >
                <option value="">{placeholder}</option>
                {options.map((opt) => (
                    <option key={opt} value={opt}>{opt}</option>
                ))}
            </select>
        ) : (
            value
        )
    );

    const renderTextareaCell = (isEditing, value, onChange) => (
        isEditing ? (
            <textarea
                className="form-control form-control-sm"
                value={value || ""}
                onChange={(e) => onChange(e.target.value)}
                rows={2}
            />
        ) : (
            value
        )
    );

    return (
        <div className="container mt-4">
            <h2 className="mb-3">Participantes</h2>

            <button
                className="btn btn-success btn-sm mb-3"
                onClick={handleCreate}
                disabled={creating}
            >
                Crear participante
            </button>

            <div className="table-responsive">
                <table className="table table-striped table-bordered">
                    <thead className="table-dark">
                        <tr>
                            <th>Actor</th>
                            <th>Entidad</th>
                            <th>Intereses / Expectativas</th>
                            <th>Rol</th>
                            <th>Contribuciones / Conflictos</th>
                            <th>Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        {participantsGeneral.length > 0 ? (
                            participantsGeneral.map((participant) => {
                                const isEditing = editingId === participant.id;
                                const data = isEditing ? editedParticipant : participant;
                                return (
                                    <tr key={participant.id}>
                                        <td>
                                            {renderSelectCell(
                                                isEditing,
                                                data.participant_actor,
                                                (v) => handleEditChange("participant_actor", v),
                                                actorOptions,
                                                "Seleccione actor"
                                            )}
                                        </td>
                                        <td>
                                            {isEditing ? (
                                                data.participant_actor === "Otro" ? (
                                                    <input
                                                        type="text"
                                                        className="form-control form-control-sm"
                                                        value={data.participant_entity || ""}
                                                        onChange={(e) => handleEditChange("participant_entity", e.target.value)}
                                                        placeholder="Escriba la entidad"
                                                    />
                                                ) : (
                                                    renderSelectCell(
                                                        true,
                                                        data.participant_entity,
                                                        (v) => handleEditChange("participant_entity", v),
                                                        getEntityOptions(data.participant_actor),
                                                        "Seleccione entidad"
                                                    )
                                                )
                                            ) : (
                                                data.participant_entity
                                            )}
                                        </td>
                                        <td>
                                            {renderTextareaCell(
                                                isEditing,
                                                data.interest_expectative,
                                                (v) => handleEditChange("interest_expectative", v)
                                            )}
                                        </td>
                                        <td>
                                            {renderSelectCell(
                                                isEditing,
                                                data.rol,
                                                (v) => handleEditChange("rol", v),
                                                rolOptions,
                                                "Seleccione rol"
                                            )}
                                        </td>
                                        <td>
                                            {renderTextareaCell(
                                                isEditing,
                                                data.contribution_conflicts,
                                                (v) => handleEditChange("contribution_conflicts", v)
                                            )}
                                        </td>
                                        <td>
                                            {isEditing ? (
                                                <div>
                                                    <button
                                                        className="btn btn-sm btn-success me-2"
                                                        onClick={handleSaveEdit}
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
                                                        onClick={() => handleEdit(participant)}
                                                    >
                                                        Editar
                                                    </button>
                                                    <button
                                                        className="btn btn-sm btn-danger"
                                                        onClick={() => handleDeleteParticipant(participant.id)}
                                                    >
                                                        Eliminar
                                                    </button>
                                                </div>
                                            )}
                                        </td>
                                    </tr>
                                );
                            })
                        ) : (
                            !creating && (
                                <tr>
                                    <td colSpan="6" className="text-center">
                                        No hay participantes para este proyecto.
                                    </td>
                                </tr>
                            )
                        )}

                        {/* Fila de creación inline */}
                        {creating && (
                            <tr>
                                <td>
                                    <select
                                        className="form-control form-control-sm"
                                        value={newParticipant.participant_actor}
                                        onChange={(e) => handleNewChange("participant_actor", e.target.value)}
                                    >
                                        <option value="">Seleccione actor</option>
                                        {actorOptions.map((a) => (
                                            <option key={a} value={a}>{a}</option>
                                        ))}
                                    </select>
                                </td>
                                <td>
                                    {newParticipant.participant_actor === "Otro" ? (
                                        <input
                                            type="text"
                                            className="form-control form-control-sm"
                                            value={newParticipant.participant_entity}
                                            onChange={(e) => handleNewChange("participant_entity", e.target.value)}
                                            placeholder="Escriba la entidad"
                                        />
                                    ) : (
                                        <select
                                            className="form-control form-control-sm"
                                            value={newParticipant.participant_entity}
                                            onChange={(e) => handleNewChange("participant_entity", e.target.value)}
                                            disabled={!newParticipant.participant_actor}
                                        >
                                            <option value="">Seleccione entidad</option>
                                            {getEntityOptions(newParticipant.participant_actor).map((e) => (
                                                <option key={e} value={e}>{e}</option>
                                            ))}
                                        </select>
                                    )}
                                </td>
                                <td>
                                    <textarea
                                        className="form-control form-control-sm"
                                        value={newParticipant.interest_expectative}
                                        onChange={(e) => handleNewChange("interest_expectative", e.target.value)}
                                        rows={2}
                                    />
                                </td>
                                <td>
                                    <select
                                        className="form-control form-control-sm"
                                        value={newParticipant.rol}
                                        onChange={(e) => handleNewChange("rol", e.target.value)}
                                    >
                                        <option value="">Seleccione rol</option>
                                        {rolOptions.map((r) => (
                                            <option key={r} value={r}>{r}</option>
                                        ))}
                                    </select>
                                </td>
                                <td>
                                    <textarea
                                        className="form-control form-control-sm"
                                        value={newParticipant.contribution_conflicts}
                                        onChange={(e) => handleNewChange("contribution_conflicts", e.target.value)}
                                        rows={2}
                                    />
                                </td>
                                <td>
                                    <button className="btn btn-sm btn-success me-2" onClick={saveNewParticipant}>
                                        Guardar
                                    </button>
                                    <button
                                        className="btn btn-sm btn-secondary"
                                        onClick={() => setCreating(false)}
                                    >
                                        Cancelar
                                    </button>
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>


            <div className="mb-3">
                <label className="form-label">Análisis de los participantes</label>
                <textarea
                    className="form-control"
                    value={analysis}
                    onChange={(e) => setAnalysis(e.target.value)}
                />
            </div>

            <button type="submit" className="btn btn-primary me-2" onClick={handleSubmit}>
                {generalId ? "Actualizar Participantes" : "Crear Participantes"}
            </button>

            <button
                type="button"
                className="btn btn-secondary"
                onClick={() => navigate("/projects")}
            >
                Regresar a Proyectos
            </button>
        </div>
    );
}

export default ParticipantsGeneral;
