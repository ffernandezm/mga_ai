import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../services/api";

function CreateParticipant() {
    const { projectId } = useParams(); // Suponiendo que usas /projects/:projectId/create-participant
    const navigate = useNavigate();

    const [formData, setFormData] = useState({
        participant_analysis: "",
        interest_expectative: "",
        rol: "",
        contribution_conflicts: "",
    });

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        try {
            const payload = {
                ...formData,
                project_id: parseInt(projectId), // Asegúrate que esté en el backend
            };

            await api.post("/participants/", payload);
            navigate(`/projects/${projectId}/participants`);
        } catch (error) {
            console.error("Error al crear participante:", error);
            alert("Hubo un error al crear el participante.");
        }
    };

    return (
        <div className="container mt-4">
            <h2>Crear Participante</h2>
            <form onSubmit={handleSubmit}>
                <div className="mb-3">
                    <label className="form-label">Análisis del Participante</label>
                    <textarea
                        className="form-control"
                        name="participant_analysis"
                        value={formData.participant_analysis}
                        onChange={handleChange}
                        required
                    ></textarea>
                </div>

                <div className="mb-3">
                    <label className="form-label">Intereses / Expectativas</label>
                    <textarea
                        className="form-control"
                        name="interest_expectative"
                        value={formData.interest_expectative}
                        onChange={handleChange}
                        required
                    ></textarea>
                </div>

                <div className="mb-3">
                    <label className="form-label">Rol</label>
                    <input
                        type="text"
                        className="form-control"
                        name="rol"
                        value={formData.rol}
                        onChange={handleChange}
                        required
                    />
                </div>

                <div className="mb-3">
                    <label className="form-label">Contribuciones / Conflictos</label>
                    <textarea
                        className="form-control"
                        name="contribution_conflicts"
                        value={formData.contribution_conflicts}
                        onChange={handleChange}
                        required
                    ></textarea>
                </div>

                <button type="submit" className="btn btn-primary">
                    Guardar Participante
                </button>

                <button
                    type="button"
                    className="btn btn-secondary ms-2"
                    onClick={() => navigate(`/projects/${projectId}/participants`)}
                >
                    Cancelar
                </button>
            </form>
        </div>
    );
}

export default CreateParticipant;
