import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../services/api";

function ParticipantsGeneral({ projectId }) {
    const [participantsGeneral, setParticipantsGeneral] = useState([]);
    const navigate = useNavigate();
    const [analysis, setAnalysis] = useState("");
    const [generalId, setGeneralId] = useState(null);

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
        if (!projectId) return alert("No hay proyecto seleccionado.");
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
            alert("Participantes actualizados correctamente.");
            fetchParticipantsGeneral();
        } catch (err) {
            console.error("Error:", err);
            alert("Error al guardar la información.");
        }
    };

    const handleDeleteParticipant = async (participantId) => {
        if (!participantId) return;
        if (window.confirm("¿Estás seguro de eliminar este participante?")) {
            try {
                await api.delete(`/participants/${participantId}`);
                setParticipantsGeneral((prev) =>
                    prev.filter((p) => p.id !== participantId)
                );
            } catch (error) {
                console.error("Error al eliminar participante:", error);
                alert("Error al eliminar el participante.");
            }
        }
    };

    return (
        <div className="container mt-4">
            <h2 className="mb-3">Participantes</h2>

            <Link
                to={`/projects/${projectId}/create-participant/${generalId}`}
                className="btn btn-success mb-3"
            >
                Crear participante
            </Link>

            <div className="table-responsive">
                <table className="table table-striped table-bordered">
                    <thead className="table-dark">
                        <tr>
                            <th>Intereses / Expectativas</th>
                            <th>Rol</th>
                            <th>Contribuciones / Conflictos</th>
                            <th>Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        {participantsGeneral.length > 0 ? (
                            participantsGeneral.map((participant) => (
                                <tr key={participant.id}>
                                    <td>{participant.interest_expectative}</td>
                                    <td>{participant.rol}</td>
                                    <td>{participant.contribution_conflicts}</td>
                                    <td>
                                        <button
                                            className="btn btn-sm btn-primary me-2"
                                            onClick={() =>
                                                navigate(
                                                    `/projects/${projectId}/edit-participant/${participant.id}`
                                                )
                                            }
                                        >
                                            Editar
                                        </button>
                                        <button
                                            className="btn btn-sm btn-danger"
                                            onClick={() => handleDeleteParticipant(participant.id)}
                                        >
                                            Eliminar
                                        </button>
                                    </td>
                                </tr>
                            ))
                        ) : (
                            <tr>
                                <td colSpan="4" className="text-center">
                                    No hay participantes para este proyecto.
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
