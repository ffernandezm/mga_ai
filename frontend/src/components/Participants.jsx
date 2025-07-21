import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../services/api";

function Participants({ projectId }) {
    const [participants, setParticipants] = useState([]);
    const navigate = useNavigate();
    const [analysis, setAnalysis] = useState("");
    const [existingId, setExistingId] = useState(null);

    const fetchParticipants = async () => {
        try {
            const response = await api.get(`/participants/${projectId}`);
            const data = response.data;

            if (data.length > 0) {
                const participant = data[0]; // suponemos 1 por proyecto
                setParticipants(data);
                setAnalysis(participant.participants_analisis);
                setExistingId(participant.id);
            }
        } catch (error) {
            console.error("Error al obtener participantes:", error);
        }
    };


    useEffect(() => {
        if (projectId) {
            fetchParticipants();
        }
    }, [projectId]);

    const handleSubmit = async () => {
        const payload = {
            project_id: projectId,
            participants_analisis: analysis,
            participants: [] // opcional, vacío si no se usa
        };

        try {
            if (existingId) {
                await api.put(`/participants/${existingId}`, payload);
            } else {
                const response = await api.post(`/participants`, payload);
                setExistingId(response.data.id);
            }
            alert("Participantes actualizados correctamente.");
        } catch (error) {
            console.error("Error al guardar:", error);
            alert("Error al guardar la información.");
        }
    };


    const handleDelete = async (id) => {
        if (window.confirm("¿Estás seguro de eliminar este participante?")) {
            try {
                await api.delete(`/participants/${id}`);
                setParticipants(participants.filter((p) => p.id !== id));
            } catch (error) {
                console.error("Error al eliminar participante:", error);
                alert("Error al eliminar el participante.");
            }
        }
    };

    return (
        <div className="container mt-4">
            <h2 className="mb-3">Participantes</h2>
            <Link to={`/projects/${projectId}/create-participant`} className="btn btn-success mb-3">
                Crear participante
            </Link>

            <div className="table-responsive">
                <table className="table table-striped table-bordered">
                    <thead className="table-dark">
                        <tr>
                            <th>Análisis</th>
                            <th>Intereses / Expectativas</th>
                            <th>Rol</th>
                            <th>Contribuciones / Conflictos</th>
                            <th>Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        {participants.length > 0 ? (
                            participants.map((participant) => (
                                <tr key={participant.id}>
                                    <td>{participant.participant_analysis}</td>
                                    <td>{participant.interest_expectative}</td>
                                    <td>{participant.rol}</td>
                                    <td>{participant.contribution_conflicts}</td>
                                    <td>
                                        <button
                                            className="btn btn-sm btn-primary me-2"
                                            onClick={() =>
                                                navigate(`/projects/${projectId}/edit-participant/${participant.id}`)
                                            }
                                        >
                                            Editar
                                        </button>
                                        <button
                                            className="btn btn-sm btn-danger"
                                            onClick={() => handleDelete(participant.id)}
                                        >
                                            Eliminar
                                        </button>
                                    </td>
                                </tr>
                            ))
                        ) : (
                            <tr>
                                <td colSpan="5" className="text-center">
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
                {existingId ? "Actualizar Participantes" : "Crear Participantes"}
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

export default Participants;
