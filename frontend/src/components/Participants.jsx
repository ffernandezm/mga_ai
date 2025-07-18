import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../services/api";

function Participants({ projectId }) {
    const [participants, setParticipants] = useState([]);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchParticipants = async () => {
            try {
                const response = await api.get(`/participants/${projectId}`);
                setParticipants(response.data);
            } catch (error) {
                console.error("Error al obtener participantes:", error);
            }
        };

        if (projectId) {
            fetchParticipants();
        }
    }, [projectId]);

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
                            <th>Análisis del participante</th>
                            <th>Intereses / Expectativas</th>
                            <th>Rol</th>
                            <th>Contribuciones / Conflictos</th>
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
                ></textarea>
            </div>

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
