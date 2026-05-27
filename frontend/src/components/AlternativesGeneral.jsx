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

    const [expandedSections, setExpandedSections] = useState({
        general: true,
        table: true,
    });

    const navigate = useNavigate();

    const toggleSection = (section) => {
        setExpandedSections((prev) => ({
            ...prev,
            [section]: !prev[section],
        }));
    };

    const renderSectionHeader = (key, title) => (
        <div
            className="card-header bg-dark text-white d-flex justify-content-between align-items-center"
            style={{ cursor: "pointer" }}
            onClick={() => toggleSection(key)}
        >
            <h5 className="mb-0">{title}</h5>
            <span>{expandedSections[key] ? "▲" : "▼"}</span>
        </div>
    );

    /* ================= FUNCIÓN PARA ASEGURAR ÚNICO ACTIVO ================= */
    const enforceSingleActive = (alternativesArray, currentIndex, newActiveValue) => {
        // Si se está desmarcando el active, simplemente actualizamos esa fila sin tocar las demás
        if (!newActiveValue) {
            return alternativesArray.map((alt, idx) =>
                idx === currentIndex ? { ...alt, active: false, state: "Vacío" } : alt
            );
        }

        // Si se está marcando active = true, desactivar todas las demás y actualizar la actual
        return alternativesArray.map((alt, idx) => {
            if (idx === currentIndex) {
                return { ...alt, active: true, state: "Completo" };
            } else {
                // Solo si la otra tenía active = true, la desactivamos y ponemos estado Vacío
                return alt.active ? { ...alt, active: false, state: "Vacío" } : alt;
            }
        });
    };

    /* ================= OBTENER GENERAL ================= */
    const fetchAlternativesGeneral = async () => {
        try {
            const res = await api.get(`/alternatives_general/${projectId}`);
            const data = res.data;

            setAlternativesGeneral(data);
            setSolutionAlternatives(data.solution_alternatives);
            setCost(data.cost);
            setProfitability(data.profitability);

            // Validar consistencia: si hay más de un activo o estado incoherente, corregir
            let correctedAlternatives = (data.alternatives || []).map(a => ({
                ...a,
                isEditing: false,
                // Aseguramos que el estado coincida con active
                state: a.active ? "Completo" : "Vacío"
            }));

            // Garantizar que solo una esté activa
            let activeFound = false;
            correctedAlternatives = correctedAlternatives.map(alt => {
                if (alt.active) {
                    if (activeFound) {
                        // Ya había un activo, este se desactiva
                        return { ...alt, active: false, state: "Vacío" };
                    }
                    activeFound = true;
                    return alt;
                }
                return alt;
            });

            setAlternatives(correctedAlternatives);
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
                active: false,      // Nueva alternativa comienza inactiva
                state: "Vacío",     // Estado derivado
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
        if (field === "active") {
            // Aplicar regla de único activo y derivar estado
            const updatedAlternatives = enforceSingleActive(alternatives, index, value);
            setAlternatives(updatedAlternatives);
        } else {
            const copy = [...alternatives];
            copy[index][field] = value;
            setAlternatives(copy);
        }
    };

    const handleCancel = (index) => {
        const copy = [...alternatives];
        if (copy[index].isNew) copy.splice(index, 1);
        else copy[index].isEditing = false;
        setAlternatives(copy);
    };

    const handleSave = async (index) => {
        let alt = alternatives[index];

        // Antes de guardar, asegurar que el estado sea coherente con active
        const stateToSend = alt.active ? "Completo" : "Vacío";
        const updatedAlt = { ...alt, state: stateToSend };

        try {
            if (updatedAlt.isNew) {
                const res = await api.post("/alternatives/", {
                    name: updatedAlt.name,
                    active: updatedAlt.active,
                    state: updatedAlt.state,
                    project_id: projectId
                });

                alternatives[index] = {
                    ...res.data,
                    isEditing: false,
                    isNew: false
                };
            } else {
                await api.put(`/alternatives/${updatedAlt.id}`, {
                    name: updatedAlt.name,
                    active: updatedAlt.active,
                    state: updatedAlt.state
                });

                alternatives[index].isEditing = false;
                alternatives[index].active = updatedAlt.active;
                alternatives[index].state = updatedAlt.state;
                alternatives[index].name = updatedAlt.name;
            }

            setAlternatives([...alternatives]);
            showSuccess("Alternativa guardada correctamente.");
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
        <div className="container mt-4 mb-5">
            <h2>Alternativas Generales</h2>

            <div className="card mb-3 shadow-sm">
                {renderSectionHeader("general", "Criterios Generales")}
                {expandedSections.general && (
                    <div className="card-body">
                        <div className="form-check mb-2">
                            <input
                                type="checkbox"
                                className="form-check-input"
                                checked={solutionAlternatives}
                                onChange={e => setSolutionAlternatives(e.target.checked)}
                            />
                            <label>Soluciones alternativas</label>
                        </div>

                        <div className="form-check mb-2">
                            <input
                                type="checkbox"
                                className="form-check-input"
                                checked={cost}
                                onChange={e => setCost(e.target.checked)}
                            />
                            <label>Costo</label>
                        </div>

                        <div className="form-check mb-0">
                            <input
                                type="checkbox"
                                className="form-check-input"
                                checked={profitability}
                                onChange={e => setProfitability(e.target.checked)}
                            />
                            <label>Rentabilidad</label>
                        </div>
                    </div>
                )}
            </div>

            <div className="card mb-3 shadow-sm">
                {renderSectionHeader("table", "Alternativas")}
                {expandedSections.table && (
                    <div className="card-body">
                        <button className="btn btn-success btn-sm mb-3" onClick={handleAddAlternative}>
                            Crear Alternativa
                        </button>

                        <div className="table-responsive">
                            <table className="table table-striped table-bordered">
                                <thead className="table-dark">
                                    <tr>
                                        <th>Nombre</th>
                                        <th>Se evaluará con esta Herramienta</th>
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
                                                            onChange={e => handleChange(i, "name", e.target.value)}
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
                                                            onChange={e => handleChange(i, "active", e.target.checked)}
                                                        />
                                                    ) : (
                                                        a.active ? "Sí" : "No"
                                                    )}
                                                </td>

                                                <td>
                                                    {a.isEditing ? (
                                                        <input
                                                            type="text"
                                                            className="form-control"
                                                            value={a.active ? "Completo" : "Vacío"}
                                                            readOnly
                                                            disabled
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
                        </div>
                    </div>
                )}
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