import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

function AlternativesGeneral({ projectId }) {
    const [alternativesGeneral, setAlternativesGeneral] = useState(null);
    const [alternatives, setAlternatives] = useState([]);
    const [solutionAlternatives, setSolutionAlternatives] = useState(false);
    const [cost, setCost] = useState(false);
    const [profitability, setProfitability] = useState(false);
    const navigate = useNavigate();

    /* ================= ALTERNATIVAS GENERALES ================= */

    const fetchAlternativesGeneral = async () => {
        try {
            const response = await api.get(`/alternatives_general/${projectId}`);
            const data = response.data;

            if (data) {
                setAlternativesGeneral(data);
                setSolutionAlternatives(data.solution_alternatives);
                setCost(data.cost);
                setProfitability(data.profitability);
                fetchAlternatives(data.id);
            } else {
                setAlternativesGeneral(null);
                setAlternatives([]);
            }
        } catch (error) {
            console.error("Error al obtener alternativas generales:", error);
        }
    };

    /* ================= ALTERNATIVAS ================= */

    const fetchAlternatives = async (alternativesGeneralId) => {
        try {
            const res = await api.get("/alternatives/", {
                params: { alternatives_general_id: alternativesGeneralId },
            });

            setAlternatives(
                res.data.map((a) => ({
                    ...a,
                    isEditing: false,
                }))
            );
        } catch (err) {
            console.error("Error al obtener alternativas:", err);
        }
    };

    useEffect(() => {
        fetchAlternativesGeneral();
    }, [projectId]);

    /* ================= CRUD INLINE ================= */

    const handleAddAlternative = () => {
        setAlternatives([
            ...alternatives,
            {
                id: null,
                name: "",
                active: true,
                state: "",
                isEditing: true,
                isNew: true,
            },
        ]);
    };

    const handleEdit = (index) => {
        const copy = [...alternatives];
        copy[index].isEditing = true;
        setAlternatives(copy);
    };

    const handleChange = (index, field, value) => {
        const copy = [...alternatives];
        copy[index][field] = value;
        setAlternatives(copy);
    };

    const handleCancel = (index) => {
        const copy = [...alternatives];
        if (copy[index].isNew) {
            copy.splice(index, 1);
        } else {
            copy[index].isEditing = false;
        }
        setAlternatives(copy);
    };

    const handleSave = async (index) => {
        const alt = alternatives[index];

        try {
            if (alt.isNew) {
                const res = await api.post("/alternatives/", {
                    name: alt.name,
                    active: alt.active,
                    state: alt.state,
                    alternatives_general_id: alternativesGeneral.id,
                });

                alternatives[index] = {
                    ...res.data,
                    isEditing: false,
                    isNew: false,
                };
            } else {
                await api.put(`/alternatives/${alt.id}`, {
                    name: alt.name,
                    active: alt.active,
                    state: alt.state,
                });

                alternatives[index].isEditing = false;
            }

            setAlternatives([...alternatives]);
        } catch (err) {
            console.error("Error guardando alternativa:", err);
            alert("Error al guardar la alternativa");
        }
    };

    const handleDelete = async (id, index) => {
        if (!window.confirm("¿Eliminar esta alternativa?")) return;

        try {
            await api.delete(`/alternatives/${id}`);
            const copy = [...alternatives];
            copy.splice(index, 1);
            setAlternatives(copy);
        } catch (err) {
            console.error("Error eliminando alternativa:", err);
            alert("Error al eliminar la alternativa");
        }
    };

    /* ================= GUARDAR GENERAL ================= */

    const handleSubmit = async () => {
        const payload = {
            solution_alternatives: solutionAlternatives,
            cost,
            profitability,
            project_id: projectId,
        };

        try {
            if (alternativesGeneral) {
                await api.put(`/alternatives_general/${projectId}`, payload);
                alert("Alternativa general actualizada");
            } else {
                const res = await api.post("/alternatives_general/", payload);
                setAlternativesGeneral(res.data);
                alert("Alternativa general creada");
            }
        } catch (err) {
            console.error(err);
            alert("Error al guardar alternativas generales");
        }
    };

    /* ================= RENDER ================= */

    return (
        <div className="container mt-4">
            <h2>Alternativas Generales</h2>

            <div className="form-check mb-2">
                <input
                    type="checkbox"
                    className="form-check-input"
                    checked={solutionAlternatives}
                    onChange={(e) => setSolutionAlternatives(e.target.checked)}
                />
                <label className="form-check-label">
                    Soluciones alternativas
                </label>
            </div>

            <div className="form-check mb-2">
                <input
                    type="checkbox"
                    className="form-check-input"
                    checked={cost}
                    onChange={(e) => setCost(e.target.checked)}
                />
                <label className="form-check-label">Costo</label>
            </div>

            <div className="form-check mb-4">
                <input
                    type="checkbox"
                    className="form-check-input"
                    checked={profitability}
                    onChange={(e) => setProfitability(e.target.checked)}
                />
                <label className="form-check-label">Rentabilidad</label>
            </div>

            <h3>Alternativas</h3>
            <button className="btn btn-success mb-3" onClick={handleAddAlternative}>
                Crear Alternativa
            </button>

            <table className="table table-bordered">
                <thead className="table-dark">
                    <tr>
                        <th>Nombre</th>
                        <th>Activo</th>
                        <th>Estado</th>
                        <th>Acciones</th>
                    </tr>
                </thead>
                <tbody>
                    {alternatives.length > 0 ? (
                        alternatives.map((a, i) => (
                            <tr key={i}>
                                <td>
                                    {a.isEditing ? (
                                        <input
                                            className="form-control"
                                            value={a.name}
                                            onChange={(e) =>
                                                handleChange(i, "name", e.target.value)
                                            }
                                        />
                                    ) : (
                                        a.name
                                    )}
                                </td>

                                <td className="text-center">
                                    {a.isEditing ? (
                                        <input
                                            type="checkbox"
                                            checked={a.active}
                                            onChange={(e) =>
                                                handleChange(i, "active", e.target.checked)
                                            }
                                        />
                                    ) : (
                                        a.active ? "Sí" : "No"
                                    )}
                                </td>

                                <td>
                                    {a.isEditing ? (
                                        <input
                                            className="form-control"
                                            value={a.state || ""}
                                            onChange={(e) =>
                                                handleChange(i, "state", e.target.value)
                                            }
                                        />
                                    ) : (
                                        a.state
                                    )}
                                </td>

                                <td>
                                    {a.isEditing ? (
                                        <>
                                            <button
                                                className="btn btn-success btn-sm me-2"
                                                onClick={() => handleSave(i)}
                                            >
                                                Guardar
                                            </button>
                                            <button
                                                className="btn btn-secondary btn-sm"
                                                onClick={() => handleCancel(i)}
                                            >
                                                Cancelar
                                            </button>
                                        </>
                                    ) : (
                                        <>
                                            <button
                                                className="btn btn-primary btn-sm me-2"
                                                onClick={() => handleEdit(i)}
                                            >
                                                Editar
                                            </button>
                                            <button
                                                className="btn btn-danger btn-sm"
                                                onClick={() => handleDelete(a.id, i)}
                                            >
                                                Eliminar
                                            </button>
                                        </>
                                    )}
                                </td>
                            </tr>
                        ))
                    ) : (
                        <tr>
                            <td colSpan="4" className="text-center">
                                No hay alternativas registradas
                            </td>
                        </tr>
                    )}
                </tbody>
            </table>

            <div className="mt-4">
                <button
                    className="btn btn-secondary me-2"
                    onClick={() => navigate("/projects")}
                >
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
