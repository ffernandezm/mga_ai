import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../services/api";
import populationOptions from "../data/populationOptions";

function CreateInterventionPopulation() {
    const { projectId, InterventionPopulationId } = useParams();

    const navigate = useNavigate();

    const [formData, setFormData] = useState({
        region: "",
        department: "",
        city: "",
        population_center: "",
        location_entity: "",
    });

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value,
            ...(name === "region" && { department: "", city: "" }),
            ...(name === "department" && { city: "" })
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const payload = {
                region: formData.region,
                department: formData.department,
                city: formData.city,
                population_center: formData.population_center,
                location_entity: formData.location_entity,
                population_id: parseInt(InterventionPopulationId, 10), // 👈 necesario
            };
            await api.post("/intervention_population/", payload);
            navigate(`/projects/${projectId}/intervention_population`);
        } catch (error) {
            console.error("Error al crear registro afectado:", error);
            alert("Hubo un error al crear el registro.");
        }
    };

    const { regions, departments, cities, populationCenters, locationEntities } = populationOptions;

    const departmentOptions = departments[formData.region] || [];
    const cityOptions = cities[formData.department] || [];

    return (
        <div className="container mt-4">
            <h2>Crear Registro Afectado</h2>
            <form onSubmit={handleSubmit}>
                <div className="mb-3">
                    <label className="form-label">Región</label>
                    <select
                        className="form-control"
                        name="region"
                        value={formData.region}
                        onChange={handleChange}
                        required
                    >
                        <option value="">Seleccione una región</option>
                        {regions.map((region) => (
                            <option key={region} value={region}>{region}</option>
                        ))}
                    </select>
                </div>

                <div className="mb-3">
                    <label className="form-label">Departamento</label>
                    <select
                        className="form-control"
                        name="department"
                        value={formData.department}
                        onChange={handleChange}
                        required
                    >
                        <option value="">Seleccione un departamento</option>
                        {departmentOptions.map((dep) => (
                            <option key={dep} value={dep}>{dep}</option>
                        ))}
                    </select>
                </div>

                <div className="mb-3">
                    <label className="form-label">Ciudad</label>
                    <select
                        className="form-control"
                        name="city"
                        value={formData.city}
                        onChange={handleChange}
                        required
                    >
                        <option value="">Seleccione una ciudad</option>
                        {cityOptions.map((city) => (
                            <option key={city} value={city}>{city}</option>
                        ))}
                    </select>
                </div>

                <div className="mb-3">
                    <label className="form-label">Centro poblado</label>
                    <select
                        className="form-control"
                        name="population_center"
                        value={formData.population_center}
                        onChange={handleChange}
                        required
                    >
                        <option value="">Seleccione un centro poblado</option>
                        {populationCenters.map((pc) => (
                            <option key={pc} value={pc}>{pc}</option>
                        ))}
                    </select>
                </div>

                <div className="mb-3">
                    <label className="form-label">Localización / Tipo Etnia</label>
                    <select
                        className="form-control"
                        name="location_entity"
                        value={formData.location_entity}
                        onChange={handleChange}
                        required
                    >
                        <option value="">Seleccione una opción</option>
                        {locationEntities.map((le) => (
                            <option key={le} value={le}>{le}</option>
                        ))}
                    </select>
                </div>

                <button type="submit" className="btn btn-primary me-2">
                    Guardar Registro
                </button>
                <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => navigate(`/edit-project/${projectId}`)}
                >
                    Cancelar
                </button>
            </form>
        </div>
    );
}

export default CreateInterventionPopulation;
