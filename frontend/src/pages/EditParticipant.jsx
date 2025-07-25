import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import api from "../services/api";
import participantOptions from "../data/participantOptions";

function EditParticipant() {
    const { projectId, participantId } = useParams();
    const navigate = useNavigate();

    const [formData, setFormData] = useState({
        participant_actor: "",
        participant_entity: "",
        participant_position: "",
        participant_analysis: "",
        interest_expectative: "",
        rol: "",
        contribution_conflicts: "",
    });

    const [availableEntities, setAvailableEntities] = useState([]);

    useEffect(() => {
        const fetchParticipant = async () => {
            try {
                const response = await api.get(`/participants/${projectId}`);
                const participant = response.data.find(p => p.id === parseInt(participantId));
                if (participant) setFormData(participant);
            } catch (error) {
                console.error("Error al obtener participante:", error);
            }
        };

        fetchParticipant();
    }, [projectId, participantId]);

    useEffect(() => {
        if (formData.participant_actor) {
            setAvailableEntities(participantOptions.entidad[formData.participant_actor] || []);
        }
    }, [formData.participant_actor]);

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await api.put(`/participants/${participantId}`, {
                ...formData,
                project_id: parseInt(projectId),
            });
            // Redirigir al formulario de edición del proyecto
            navigate(`/edit-project/${projectId}`);
        } catch (error) {
            console.error("Error al actualizar participante:", error);
            alert("Hubo un error al actualizar el participante.");
        }
    };

    return (
        <div className="container mt-4">
            <h2>Editar Participante</h2>
            <form onSubmit={handleSubmit}>
                {/* Actor */}
                <div className="mb-3">
                    <label className="form-label">Actor</label>
                    <select
                        className="form-control"
                        name="participant_actor"
                        value={formData.participant_actor}
                        onChange={handleChange}
                        required
                    >
                        <option value="">Seleccione un actor</option>
                        {participantOptions.actor.map((actor) => (
                            <option key={actor} value={actor}>
                                {actor}
                            </option>
                        ))}
                    </select>
                </div>

                {/* Entidad */}
                <div className="mb-3">
                    <label className="form-label">Entidad</label>
                    <select
                        className="form-control"
                        name="participant_entity"
                        value={formData.participant_entity}
                        onChange={handleChange}
                        required
                    >
                        <option value="">Seleccione una entidad</option>
                        {availableEntities.map((entidad) => (
                            <option key={entidad} value={entidad}>
                                {entidad}
                            </option>
                        ))}
                    </select>
                </div>

                {/* Rol */}
                <div className="mb-3">
                    <label className="form-label">Rol</label>
                    <select
                        className="form-control"
                        name="rol"
                        value={formData.rol}
                        onChange={handleChange}
                        required
                    >
                        <option value="">Seleccione un rol</option>
                        {participantOptions.rol.map((rol) => (
                            <option key={rol} value={rol}>
                                {rol}
                            </option>
                        ))}
                    </select>
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
                    Guardar Cambios
                </button>
                <button
                    type="button"
                    className="btn btn-secondary ms-2"
                    onClick={() => navigate(`/edit-project/${projectId}`)}
                >
                    Cancelar
                </button>
            </form>
        </div>
    );
}

export default EditParticipant;
