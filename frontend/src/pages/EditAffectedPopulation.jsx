import { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../services/api";
import populationOptions from "../data/populationOptions";

function EditAffectedPopulation() {
    const { projectId, AffectedPopulationId } = useParams();
    const navigate = useNavigate();

    const [formData, setFormData] = useState({
        region: "",
        department: "",
        city: "",
        population_center: "",
        location_entity: "",
        population_id: null,
    });

    useEffect(() => {
        const fetchPopulation = async () => {
            try {
                const response = await api.get(`/affected_population/${AffectedPopulationId}`);
                const affected_population = response.data;
                if (affected_population) {
                    setFormData({
                        region: affected_population.region || "",
                        department: affected_population.department || "",
                        city: affected_population.city || "",
                        population_center: affected_population.population_center || "",
                        location_entity: affected_population.location_entity || "",
                        population_id: affected_population.population_id,
                    });
                }
            } catch (error) {
                console.error("Error al obtener registro:", error);
            }
        };
        fetchPopulation();
    }, [projectId, AffectedPopulationId]);

    const handleChange = (e) => {
        const { name, value } = e.target;

        // Reset dependencias si se cambia región o departamento
        if (name === "region") {
            setFormData({
                ...formData,
                region: value,
                department: "",
                city: "",
            });
        } else if (name === "department") {
            setFormData({
                ...formData,
                department: value,
                city: "",
            });
        } else {
            setFormData({ ...formData, [name]: value });
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const payload = { ...formData };
            console.log("Poblacion AFECTADA PARA ACTUALIZAR")
            console.log(payload)
            await api.put(`/affected_population/${AffectedPopulationId}`, payload);
            navigate(`/projects/${projectId}`);
        } catch (error) {
            console.error("Error al actualizar registro:", error);
            alert("Hubo un error al actualizar el registro.");
        }
    };

    const { regions, departments, cities, populationCenters, locationEntities } = populationOptions;

    const availableDepartments = departments[formData.region] || [];
    const availableCities = cities[formData.department] || [];

    return (
        <div className="container mt-4">
            <h2>Editar Registro Afectado</h2>
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
                        disabled={!formData.region}
                    >
                        <option value="">Seleccione un departamento</option>
                        {availableDepartments.map((dep) => (
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
                        disabled={!formData.department}
                    >
                        <option value="">Seleccione una ciudad</option>
                        {availableCities.map((city) => (
                            <option key={city} value={city}>{city}</option>
                        ))}
                    </select>
                </div>

                <div className="mb-3">
                    <label className="form-label">Centro Poblado</label>
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
                    Guardar Cambios
                </button>
                <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => navigate(`/projects/${projectId}`)}
                >
                    Cancelar
                </button>
            </form>
        </div>
    );
}

export default EditAffectedPopulation;
