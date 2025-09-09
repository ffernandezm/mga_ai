import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../services/api";

function Population({ projectId }) {
    const [affectedPopulation, setAffectedPopulation] = useState([]);
    const [interventionPopulation, setInterventionPopulation] = useState([]);
    const [characteristicsPopulation, setCharacteristicsPopulation] = useState([]);
    const [analysis, setAnalysis] = useState("");
    const [populationId, setPopulationId] = useState(null);
    const navigate = useNavigate();

    const fetchPopulation = async () => {
        try {
            const response = await api.get(`/population/${projectId}`);
            const data = response.data;

            if (data) {
                setAnalysis(data.population_json?.analysis || "");
                setPopulationId(data.id);
                setAffectedPopulation(data.affected_population || []);
                setInterventionPopulation(data.intervention_population || []);
                setCharacteristicsPopulation(data.characteristics_population || []);

                console.log("INFORMACION DE POBLACION")
                console.log(data)
            }
        } catch (error) {
            console.error("Error al obtener la Población:", error);
        }
    };

    useEffect(() => {
        if (projectId) fetchPopulation();
    }, [projectId]);

    const handleSubmit = async () => {
        if (!projectId) return alert("No hay proyecto seleccionado.");

        const payload = {
            project_id: projectId,
            population_json: { analysis },
            affected_population: affectedPopulation,
            intervention_population: interventionPopulation,
            characteristics_population: characteristicsPopulation,
        };

        try {
            if (populationId) {
                await api.put(`/population/${populationId}`, payload);
            } else {
                const res = await api.post(`/population`, payload);
                setPopulationId(res.data.id);
            }
            alert("Población actualizada correctamente.");
            fetchPopulation();
        } catch (err) {
            console.error("Error al guardar la información:", err);
            alert("Error al guardar la información.");
        }
    };

    const handleDelete = async (id, type) => {
        if (!id) return;
        if (window.confirm("¿Eliminar este registro?")) {
            try {
                const endpoint =
                    type === "affected"
                        ? `/affected_population/${id}`
                        : `/intervention_population/${id}`;

                await api.delete(endpoint);

                if (type === "affected") {
                    setAffectedPopulation(prev => prev.filter(item => item.id !== id));
                } else {
                    setInterventionPopulation(prev => prev.filter(item => item.id !== id));
                }
            } catch (error) {
                console.error("Error al eliminar registro:", error);
                alert("Error al eliminar registro.");
            }
        }
    };

    return (
        <div className="container mt-4">
            {/* Affected Population */}
            <div>
                <h2 className="mb-3">Población Afectada</h2>

                <Link
                    to={`/projects/${projectId}/create-affected-population/${populationId}`}
                    className="btn btn-success mb-3"
                >
                    Crear Registro de Afectados
                </Link>

                <div className="table-responsive">
                    <table className="table table-striped table-bordered">
                        <thead className="table-dark">
                            <tr>
                                <th>ID</th>
                                <th>Región</th>
                                <th>Departamento</th>
                                <th>Ciudad</th>
                                <th>Centro Poblado</th>
                                <th>Resguardo</th>
                                <th>Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            {affectedPopulation.length > 0 ? (
                                affectedPopulation.map((p) => (
                                    <tr key={p.id}>
                                        <td>{p.id}</td>
                                        <td>{p.region}</td>
                                        <td>{p.department}</td>
                                        <td>{p.city}</td>
                                        <td>{p.population_center}</td>
                                        <td>{p.location_entity}</td>
                                        <td>
                                            <button
                                                className="btn btn-sm btn-primary me-2"
                                                onClick={() =>
                                                    navigate(
                                                        `/projects/${projectId}/edit-affected-population/${p.id}`
                                                    )
                                                }
                                            >
                                                Editar
                                            </button>
                                            <button
                                                className="btn btn-sm btn-danger"
                                                onClick={() => handleDelete(p.id, "affected")}
                                            >
                                                Eliminar
                                            </button>
                                        </td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan="7" className="text-center">
                                        No hay registros afectados.
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Intervention Population */}
            <div className="mt-5">
                <h2 className="mb-3">Población de Intervención</h2>

                <Link
                    to={`/projects/${projectId}/create-intervention-population/${populationId}`}
                    className="btn btn-success mb-3"
                >
                    Crear Registro de Intervención
                </Link>

                <div className="table-responsive">
                    <table className="table table-striped table-bordered">
                        <thead className="table-dark">
                            <tr>
                                <th>ID</th>
                                <th>Región</th>
                                <th>Departamento</th>
                                <th>Ciudad</th>
                                <th>Centro Poblado</th>
                                <th>Resguardo</th>
                                <th>Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            {interventionPopulation.length > 0 ? (
                                interventionPopulation.map((p) => (
                                    <tr key={p.id}>
                                        <td>{p.id}</td>
                                        <td>{p.region}</td>
                                        <td>{p.department}</td>
                                        <td>{p.city}</td>
                                        <td>{p.population_center}</td>
                                        <td>{p.location_entity}</td>
                                        <td>
                                            <button
                                                className="btn btn-sm btn-primary me-2"
                                                onClick={() =>
                                                    navigate(
                                                        `/projects/${projectId}/edit-intervention-population/${p.id}`
                                                    )
                                                }
                                            >
                                                Editar
                                            </button>
                                            <button
                                                className="btn btn-sm btn-danger"
                                                onClick={() => handleDelete(p.id, "intervention")}
                                            >
                                                Eliminar
                                            </button>
                                        </td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan="7" className="text-center">
                                        No hay registros de intervención.
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Characteristics Population */}
            <div className="mt-5">
                <h2 className="mb-3">Características de la Población</h2>
                <div className="table-responsive">
                    <table className="table table-striped table-bordered">
                        <thead className="table-dark">
                            <tr>
                                <th>Clasificación</th>
                                <th>Detalle</th>
                                <th>Número de personas</th>
                                <th>Fuente de Información</th>
                                <th>Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            {characteristicsPopulation.length > 0 ? (
                                characteristicsPopulation.map((p) => (
                                    <tr key={p.id}>
                                        <td>{p.classification}</td>
                                        <td>{p.detail}</td>
                                        <td>{p.people_number}</td>
                                        <td>{p.information}</td>
                                        <td>
                                            <button
                                                className="btn btn-sm btn-primary me-2"
                                                onClick={() =>
                                                    navigate(
                                                        `/projects/${projectId}/edit-intervention-population/${p.id}`
                                                    )
                                                }
                                            >
                                                Editar
                                            </button>
                                            <button
                                                className="btn btn-sm btn-danger"
                                                onClick={() => handleDelete(p.id, "intervention")}
                                            >
                                                Guardar
                                            </button>
                                        </td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan="7" className="text-center">
                                        No hay registros de intervención.
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            <div className="mt-4">
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

export default Population;
