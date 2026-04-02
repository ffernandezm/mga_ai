import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";
import { useNotification } from "../context/NotificationContext";

function AlternativesGeneral({ projectId }) {
    const { showSuccess, showError, showConfirmation } = useNotification();
    const [alternativesGeneral, setAlternativesGeneral] = useState(null);
    const [alternatives, setAlternatives] = useState([]);
    const [solutionAlternatives, setSolutionAlternatives] = useState(false);
    const [cost, setCost] = useState(false);
    const [profitability, setProfitability] = useState(false);

    const navigate = useNavigate();

    /* ================= OBTENER GENERAL ================= */

    const fetchAlternativesGeneral = async () => {
        try {
            const res = await api.get(`/alternatives_general/${projectId}`);
            const data = res.data;

            setAlternativesGeneral(data);
            setSolutionAlternatives(data.solution_alternatives);
            setCost(data.cost);
            setProfitability(data.profitability);

            // 👇 ya vienen anidadas
            setAlternatives(
                (data.alternatives || []).map(a => ({
                    ...a,
                    isEditing: false
                }))
            );

        } catch (error) {
            setAlternativesGeneral(null);
            setAlternatives([]);
        }
    };

    useEffect(() => {
        fetchAlternativesGeneral();
    }, [projectId]);

    /* ================= CRUD ALTERNATIVAS ================= */

    const handleAddAlternative = () => {
        if (!alternativesGeneral) {
            showError("Primero debes guardar las alternativas generales");
            return;
        }

        setAlternatives([
            ...alternatives,
            {
                id: null,
                name: "",
                active: true,
                state: "",
                isEditing: true,
                isNew: true
            }
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
        if (copy[index].isNew) copy.splice(index, 1);
        else copy[index].isEditing = false;
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
                    project_id: projectId   // ✅ CORRECTO
                });

                alternatives[index] = {
                    ...res.data,
                    isEditing: false,
                    isNew: false
                };

            } else {

                await api.put(`/alternatives/${alt.id}`, {
                    name: alt.name,
                    active: alt.active,
                    state: alt.state
                });

                alternatives[index].isEditing = false;
            }

            setAlternatives([...alternatives]);

        } catch (err) {
            console.error(err);
            showError("Error guardando alternativa");
        }
    };

    const handleDelete = async (id, index) => {
        const confirmed = await showConfirmation({
            title: "Eliminar Alternativa",
            message: "¿Eliminar esta alternativa?"
        });
        if (!confirmed) return;

        try {
            await api.delete(`/alternatives/${id}`);
            const copy = [...alternatives];
            copy.splice(index, 1);
            setAlternatives(copy);
            showSuccess("Alternativa eliminada correctamente.");
        } catch (err) {
            showError("Error eliminando alternativa");
        }
    };

    /* ================= GUARDAR GENERAL ================= */

    const handleSubmit = async () => {

        const payload = {
            solution_alternatives: solutionAlternatives,
            cost,
            profitability,
            project_id: projectId
        };

        try {

            if (alternativesGeneral) {

                await api.put(`/alternatives_general/${projectId}`, payload);
                showSuccess("Actualizado correctamente.");

            } else {

                const res = await api.post("/alternatives_general/", payload);
                setAlternativesGeneral(res.data);
                showSuccess("Creado correctamente.");
            }

        } catch (err) {
            showError("Error guardando");
        }
    };

    /* ================= RENDER ================= */

    return (
        <div className="container mt-4">

            <h2>Alternativas Generales</h2>

            <div className="form-check mb-2">
                <input type="checkbox"
                    className="form-check-input"
                    checked={solutionAlternatives}
                    onChange={e => setSolutionAlternatives(e.target.checked)}
                />
                <label>Soluciones alternativas</label>
            </div>

            <div className="form-check mb-2">
                <input type="checkbox"
                    className="form-check-input"
                    checked={cost}
                    onChange={e => setCost(e.target.checked)}
                />
                <label>Costo</label>
            </div>

            <div className="form-check mb-4">
                <input type="checkbox"
                    className="form-check-input"
                    checked={profitability}
                    onChange={e => setProfitability(e.target.checked)}
                />
                <label>Rentabilidad</label>
            </div>

            <h3>Alternativas</h3>

            <button className="btn btn-success btn-sm mb-3"
                onClick={handleAddAlternative}>
                Crear Alternativa
            </button>

            <div className="table-responsive">
                <table className="table table-striped table-bordered">
                    <thead className="table-dark">
                        <tr>
                            <th>Nombre</th>
                            <th>Activo</th>
                            <th>Estado</th>
                            <th>Acciones</th>
                        </tr>
                    </thead>

                    <tbody>
                        {alternatives.length > 0 ? alternatives.map((a, i) => (

                            <tr key={i}>

                                <td>
                                    {a.isEditing
                                        ? <input className="form-control"
                                            value={a.name}
                                            onChange={e => handleChange(i, "name", e.target.value)}
                                        />
                                        : a.name}
                                </td>

                                <td className="text-center">
                                    {a.isEditing
                                        ? <input type="checkbox"
                                            checked={a.active}
                                            onChange={e => handleChange(i, "active", e.target.checked)}
                                        />
                                        : a.active ? "Sí" : "No"}
                                </td>

                                <td>
                                    {a.isEditing
                                        ? <input className="form-control"
                                            value={a.state || ""}
                                            onChange={e => handleChange(i, "state", e.target.value)}
                                        />
                                        : a.state}
                                </td>

                                <td>
                                    {a.isEditing ? (
                                        <>
                                            <button className="btn btn-success btn-sm me-2"
                                                onClick={() => handleSave(i)}>
                                                Guardar
                                            </button>

                                            <button className="btn btn-secondary btn-sm"
                                                onClick={() => handleCancel(i)}>
                                                Cancelar
                                            </button>
                                        </>
                                    ) : (
                                        <>
                                            <button className="btn btn-primary btn-sm me-2"
                                                onClick={() => handleEdit(i)}>
                                                Editar
                                            </button>

                                            <button className="btn btn-danger btn-sm"
                                                onClick={() => handleDelete(a.id, i)}>
                                                Eliminar
                                            </button>
                                        </>
                                    )}
                                </td>

                            </tr>

                        )) : (
                            <tr>
                                <td colSpan="4" className="text-center">
                                    No hay alternativas registradas
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>

            <div className="mt-4">
                <button className="btn btn-secondary me-2"
                    onClick={() => navigate("/projects")}>
                    Regresar
                </button>

                <button className="btn btn-primary"
                    onClick={handleSubmit}>
                    Guardar Cambios
                </button>
            </div>

        </div>
    );
}

export default AlternativesGeneral;