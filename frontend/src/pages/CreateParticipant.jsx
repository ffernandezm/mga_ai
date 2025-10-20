import { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../services/api";
import participantOptions from "../data/participantOptions";

function CreateParticipant() {
    const { projectId, generalId } = useParams(); // ✅ generalId viene de ParticipantsGeneral
    const navigate = useNavigate();

    const [formData, setFormData] = useState({
        participant_actor: "",
        participant_entity: "",
        interest_expectative: "",
        rol: "",
        contribution_conflicts: "",
    });

    const [availableEntities, setAvailableEntities] = useState([]);

    useEffect(() => {
        if (formData.participant_actor) {
            setAvailableEntities(
                participantOptions.entidad[formData.participant_actor] || []
            );
        } else {
            setAvailableEntities([]);
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
            const payload = {
                ...formData,
                participants_general_id: parseInt(generalId),
            };
            await api.post("/participants/", payload);

            // ✅ Redirige al formulario con el tab de participantes activo
            navigate(`/projects/${projectId}/formulation?tab=participants_general`);
        } catch (error) {
            console.error("Error al crear participante:", error);
            alert("Hubo un error al crear el participante.");
        }
    };

    return (
        <div className="container mt-4">
            <h2>Crear Participante</h2>
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

                {/* Intereses */}
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

                {/* Contribuciones */}
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

                {/* 👇 Ajuste para volver al mismo tab */}
                <button
                    type="button"
                    className="btn btn-secondary ms-2"
                    onClick={() =>
                        navigate(`/projects/${projectId}/formulation?tab=participants_general`)
                    }
                >
                    Cancelar
                </button>
            </form>
        </div>
    );
}

export default CreateParticipant;
