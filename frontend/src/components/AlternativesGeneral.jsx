import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../services/api";

function AlternativesGeneral({ projectId }) {
    const [alternativesGeneral, setAlternativesGeneral] = useState([]);
    const [alternatives, setAlternatives] = useState([]);
    const [solutionAlternatives, setSolutionAlternatives] = useState(false);
    const [cost, setCost] = useState(false);
    const [profitability, setProfitability] = useState(false);
    const [alternativeId, setAlternativeId] = useState(null);
    const navigate = useNavigate();

    const fetchAlternativesGeneral = async () => {
        try {
            const response = await api.get(`/alternatives-general`);
            const data = response.data;

            if (data && data.length > 0) {
                const general = data[0];
                setAlternativesGeneral(data);
                setAlternativeId(general.id);
                setSolutionAlternatives(general.solution_alternatives);
                setCost(general.cost);
                setProfitability(general.profitability);
                setAlternatives(general.alternatives || []);
            }
        } catch (error) {
            console.error("Error al obtener las alternativas generales:", error);
        }
    };

    useEffect(() => {
        fetchAlternativesGeneral();
    }, [projectId]);

    const handleSubmit = async () => {
        const payload = {
            solution_alternatives: solutionAlternatives,
            cost,
            profitability,
            alternatives,
        };

        try {
            if (alternativeId) {
                await api.put(`/alternatives-general/${alternativeId}`, payload);
            } else {
                const res = await api.post(`/alternatives-general`, payload);
                setAlternativeId(res.data.id);
            }
            alert("Alternativa general guardada correctamente.");
            fetchAlternativesGeneral();
        } catch (err) {
            console.error("Error al guardar la alternativa:", err);
            alert("Error al guardar la alternativa.");
        }
    };

    const handleDeleteAlternative = async (id) => {
        if (!id) return;
        if (window.confirm("¿Eliminar esta alternativa?")) {
            try {
                await api.delete(`/alternatives/${id}`);
                setAlternatives(prev => prev.filter(a => a.id !== id));
            } catch (error) {
                console.error("Error al eliminar alternativa:", error);
                alert("Error al eliminar alternativa.");
            }
        }
    };

    return (
        <div className="container mt-4">
            <h2>Alternativas Generales</h2>
            <div className="form-check mb-2">
                <input
                    className="form-check-input"
                    type="checkbox"
                    checked={solutionAlternatives}
                    onChange={(e) => setSolutionAlternatives(e.target.checked)}
                    id="solutionAlternatives"
                />
                <label className="form-check-label" htmlFor="solutionAlternatives">
                    Soluciones alternativas
                </label>
            </div>
            <div className="form-check mb-2">
                <input
                    className="form-check-input"
                    type="checkbox"
                    checked={cost}
                    onChange={(e) => setCost(e.target.checked)}
                    id="cost"
                />
                <label className="form-check-label" htmlFor="cost">
                    Costo
                </label>
            </div>
            <div className="form-check mb-4">
                <input
                    className="form-check-input"
                    type="checkbox"
                    checked={profitability}
                    onChange={(e) => setProfitability(e.target.checked)}
                    id="profitability"
                />
                <label className="form-check-label" htmlFor="profitability">
                    Rentabilidad
                </label>
            </div>

            {/* Tabla de Alternatives */}
            <div className="mb-5">
                <h2>Alternativas</h2>
                <Link
                    to={`/projects/${projectId}/create-alternative/${alternativeId}`}
                    className="btn btn-success mb-3"
                >
                    Crear Alternativa
                </Link>
                <div className="table-responsive">
                    <table className="table table-striped table-bordered">
                        <thead className="table-dark">
                            <tr>
                                <th>ID</th>
                                <th>Nombre</th>
                                <th>Activo</th>
                                <th>Estado</th>
                                <th>Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            {alternatives.length > 0 ? (
                                alternatives.map((a) => (
                                    <tr key={a.id}>
                                        <td>{a.id}</td>
                                        <td>{a.name}</td>
                                        <td>{a.active ? "Sí" : "No"}</td>
                                        <td>{a.state}</td>
                                        <td>
                                            <button
                                                className="btn btn-sm btn-primary me-2"
                                                onClick={() =>
                                                    navigate(
                                                        `/projects/${projectId}/edit-alternative/${a.id}`
                                                    )
                                                }
                                            >
                                                Editar
                                            </button>
                                            <button
                                                className="btn btn-sm btn-danger"
                                                onClick={() => handleDeleteAlternative(a.id)}
                                            >
                                                Eliminar
                                            </button>
                                        </td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan="5" className="text-center">
                                        No hay alternativas registradas.
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

export default AlternativesGeneral;
