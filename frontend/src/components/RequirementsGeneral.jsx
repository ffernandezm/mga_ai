import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";
import { useNotification } from "../context/NotificationContext";
import unidadesCsv from "../data/unidades.csv?raw";

const unitOptions = unidadesCsv
    .split("\n")
    .slice(1)
    .map((line) => line.split(";")[0].trim())
    .filter(Boolean);

function RequirementsGeneral({ projectId }) {
    const navigate = useNavigate();
    const { showSuccess, showError, showConfirmation } = useNotification();
    const [requirementsGeneralId, setRequirementsGeneralId] = useState(null);
    const [requirementsAnalysis, setRequirementsAnalysis] = useState("");
    const [requirements, setRequirements] = useState([]);

    // Estado para controlar qué sección está desplegada
    const [expandedSections, setExpandedSections] = useState({
        analysis: true,
        table: true
    });

    const toggleSection = (section) => {
        setExpandedSections((prev) => ({
            ...prev,
            [section]: !prev[section]
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

    // ---------- EDICIÓN ----------
    const [editingRequirementId, setEditingRequirementId] = useState(null);
    const [editedRequirement, setEditedRequirement] = useState({});

    // ---------- CREACIÓN ----------
    const [creatingRequirement, setCreatingRequirement] = useState(false);
    const [newRequirement, setNewRequirement] = useState({
        good_service_name: "",
        good_service_description: "",
        supply_description: "",
        demand_description: "",
        unit_of_measure: "",
        start_year: "",
        end_year: "",
        last_projected_year: ""
    });

    // ---------- FETCH ----------
    const fetchRequirementsGeneral = async () => {
        try {
            const res = await api.get(`/requirements_general/${projectId}`);
            if (res.data) {
                setRequirementsGeneralId(res.data.id);
                setRequirementsAnalysis(res.data.analysis || "");
                setRequirements(res.data.requirements || []);
            }
        } catch (error) {
            if (error.response?.status !== 404) {
                console.error("Error cargando necesidades generales:", error);
            }
        }
    };

    useEffect(() => {
        if (projectId) {
            fetchRequirementsGeneral();
        }
    }, [projectId]);

    // ---------- HANDLERS PARA CRUD ----------
    const handleEdit = (requirement) => {
        setEditingRequirementId(requirement.id);
        setEditedRequirement({ ...requirement });
    };

    const handleSave = async () => {
        try {
            await api.put(`/requirements/${editingRequirementId}`, editedRequirement);
            setRequirements(requirements.map(r => r.id === editingRequirementId ? editedRequirement : r));
            setEditingRequirementId(null);
            showSuccess("Necesidad actualizada exitosamente");
        } catch (error) {
            console.error(error);
            showError("Error al actualizar la necesidad");
        }
    };

    const cancelEdit = () => {
        setEditingRequirementId(null);
        setEditedRequirement({});
    };

    const handleDelete = (id) => {
        showConfirmation("¿Desea eliminar esta necesidad?", async () => {
            try {
                await api.delete(`/requirements/${id}`);
                setRequirements(requirements.filter(r => r.id !== id));
                showSuccess("Necesidad eliminada exitosamente");
            } catch (error) {
                console.error(error);
                showError("Error al eliminar la necesidad");
            }
        });
    };

    const saveNewRequirement = async () => {
        if (!newRequirement.good_service_name || !newRequirement.unit_of_measure) {
            showError("Por favor complete los campos requeridos");
            return;
        }

        try {
            const res = await api.post(`/requirements/`, {
                ...newRequirement,
                requirements_general_id: requirementsGeneralId
            });
            setRequirements([...requirements, res.data]);
            setNewRequirement({
                good_service_name: "",
                good_service_description: "",
                supply_description: "",
                demand_description: "",
                unit_of_measure: "",
                start_year: "",
                end_year: "",
                last_projected_year: ""
            });
            setCreatingRequirement(false);
            showSuccess("Necesidad creada exitosamente");
        } catch (error) {
            console.error(error);
            showError("Error al crear la necesidad");
        }
    };

    // ---------- GUARDAR ----------
    const handleSubmit = async () => {
        const payload = {
            analysis: requirementsAnalysis,
            project_id: projectId
        };

        try {
            if (requirementsGeneralId) {
                // Actualizar (PUT)
                await api.put(`/requirements_general/${projectId}`, payload);
            } else {
                // Crear (POST)
                const res = await api.post(`/requirements_general/`, payload);
                setRequirementsGeneralId(res.data.id);
            }
            showSuccess("Necesidades generales guardadas exitosamente");
        } catch (error) {
            console.error(error);
            showError("Error al guardar las necesidades generales");
        }
    };

    return (
        <div className="container mt-4 mb-5">
            <h2 className="mb-4">Necesidades Generales</h2>

            {/* SECCIÓN 1: ANÁLISIS */}
            <div className="card mb-3 shadow-sm">
                {renderSectionHeader("analysis", "Análisis de Necesidades")}
                {expandedSections.analysis && (
                    <div className="card-body">
                        <textarea
                            className="form-control"
                            rows="4"
                            value={requirementsAnalysis}
                            onChange={(e) => setRequirementsAnalysis(e.target.value)}
                            placeholder="Ingrese el análisis de necesidades..."
                        />
                    </div>
                )}
            </div>

            {/* SECCIÓN 2: TABLA DE NECESIDADES */}
            <div className="card mb-3 shadow-sm">
                {renderSectionHeader("table", "Necesidades")}
                {expandedSections.table && (
                    <div className="card-body">
                        <div className="table-responsive">
                            <table className="table table-striped table-bordered">
                                <thead className="table-dark">
                                    <tr>
                                        <th>ID</th>
                                        <th>Bien o Servicio</th>
                                        <th>Descripción</th>
                                        <th>Oferta</th>
                                        <th>Demanda</th>
                                        <th>Unidad</th>
                                        <th>Año Inicio</th>
                                        <th>Año Final</th>
                                        <th>Último Año</th>
                                        <th>Acciones</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {requirements.map(r => (
                                        <tr key={r.id}>
                                            <td>{r.id}</td>
                                            <td>
                                                {editingRequirementId === r.id ? (
                                                    <input
                                                        className="form-control form-control-sm"
                                                        value={editedRequirement.good_service_name || ""}
                                                        onChange={e => setEditedRequirement({ ...editedRequirement, good_service_name: e.target.value })}
                                                    />
                                                ) : r.good_service_name}
                                            </td>
                                            <td>
                                                {editingRequirementId === r.id ? (
                                                    <textarea
                                                        className="form-control form-control-sm"
                                                        value={editedRequirement.good_service_description || ""}
                                                        onChange={e => setEditedRequirement({ ...editedRequirement, good_service_description: e.target.value })}
                                                    />
                                                ) : r.good_service_description}
                                            </td>
                                            <td>
                                                {editingRequirementId === r.id ? (
                                                    <textarea
                                                        className="form-control form-control-sm"
                                                        value={editedRequirement.supply_description || ""}
                                                        onChange={e => setEditedRequirement({ ...editedRequirement, supply_description: e.target.value })}
                                                    />
                                                ) : r.supply_description}
                                            </td>
                                            <td>
                                                {editingRequirementId === r.id ? (
                                                    <textarea
                                                        className="form-control form-control-sm"
                                                        value={editedRequirement.demand_description || ""}
                                                        onChange={e => setEditedRequirement({ ...editedRequirement, demand_description: e.target.value })}
                                                    />
                                                ) : r.demand_description}
                                            </td>
                                            <td>
                                                {editingRequirementId === r.id ? (
                                                    <select
                                                        className="form-control form-control-sm"
                                                        value={editedRequirement.unit_of_measure || ""}
                                                        onChange={e => setEditedRequirement({ ...editedRequirement, unit_of_measure: e.target.value })}
                                                    >
                                                        <option value="">Seleccione unidad</option>
                                                        {unitOptions.map(u => (
                                                            <option key={u} value={u}>{u}</option>
                                                        ))}
                                                    </select>
                                                ) : r.unit_of_measure}
                                            </td>
                                            <td>
                                                {editingRequirementId === r.id ? (
                                                    <input
                                                        type="number"
                                                        className="form-control form-control-sm"
                                                        value={editedRequirement.start_year || ""}
                                                        onChange={e => setEditedRequirement({ ...editedRequirement, start_year: e.target.value })}
                                                    />
                                                ) : r.start_year}
                                            </td>
                                            <td>
                                                {editingRequirementId === r.id ? (
                                                    <input
                                                        type="number"
                                                        className="form-control form-control-sm"
                                                        value={editedRequirement.end_year || ""}
                                                        onChange={e => setEditedRequirement({ ...editedRequirement, end_year: e.target.value })}
                                                    />
                                                ) : r.end_year}
                                            </td>
                                            <td>
                                                {editingRequirementId === r.id ? (
                                                    <input
                                                        type="number"
                                                        className="form-control form-control-sm"
                                                        value={editedRequirement.last_projected_year || ""}
                                                        onChange={e => setEditedRequirement({ ...editedRequirement, last_projected_year: e.target.value })}
                                                    />
                                                ) : r.last_projected_year}
                                            </td>
                                            <td>
                                                {editingRequirementId === r.id ? (
                                                    <>
                                                        <button className="btn btn-sm btn-success me-2" onClick={handleSave}>Guardar</button>
                                                        <button className="btn btn-sm btn-secondary" onClick={cancelEdit}>Cancelar</button>
                                                    </>
                                                ) : (
                                                    <>
                                                        <button className="btn btn-sm btn-primary me-2" onClick={() => handleEdit(r)}>Editar</button>
                                                        <button className="btn btn-sm btn-danger" onClick={() => handleDelete(r.id)}>Eliminar</button>
                                                    </>
                                                )}
                                            </td>
                                        </tr>
                                    ))}
                                    {creatingRequirement && (
                                        <tr>
                                            <td>Nuevo</td>
                                            <td>
                                                <input
                                                    className="form-control form-control-sm"
                                                    value={newRequirement.good_service_name}
                                                    onChange={e => setNewRequirement({ ...newRequirement, good_service_name: e.target.value })}
                                                />
                                            </td>
                                            <td>
                                                <textarea
                                                    className="form-control form-control-sm"
                                                    value={newRequirement.good_service_description}
                                                    onChange={e => setNewRequirement({ ...newRequirement, good_service_description: e.target.value })}
                                                />
                                            </td>
                                            <td>
                                                <textarea
                                                    className="form-control form-control-sm"
                                                    value={newRequirement.supply_description}
                                                    onChange={e => setNewRequirement({ ...newRequirement, supply_description: e.target.value })}
                                                />
                                            </td>
                                            <td>
                                                <textarea
                                                    className="form-control form-control-sm"
                                                    value={newRequirement.demand_description}
                                                    onChange={e => setNewRequirement({ ...newRequirement, demand_description: e.target.value })}
                                                />
                                            </td>
                                            <td>
                                                <select
                                                    className="form-control form-control-sm"
                                                    value={newRequirement.unit_of_measure}
                                                    onChange={e => setNewRequirement({ ...newRequirement, unit_of_measure: e.target.value })}
                                                >
                                                    <option value="">Seleccione unidad</option>
                                                    {unitOptions.map(u => (
                                                        <option key={u} value={u}>{u}</option>
                                                    ))}
                                                </select>
                                            </td>
                                            <td>
                                                <input
                                                    type="number"
                                                    className="form-control form-control-sm"
                                                    value={newRequirement.start_year}
                                                    onChange={e => setNewRequirement({ ...newRequirement, start_year: e.target.value })}
                                                />
                                            </td>
                                            <td>
                                                <input
                                                    type="number"
                                                    className="form-control form-control-sm"
                                                    value={newRequirement.end_year}
                                                    onChange={e => setNewRequirement({ ...newRequirement, end_year: e.target.value })}
                                                />
                                            </td>
                                            <td>
                                                <input
                                                    type="number"
                                                    className="form-control form-control-sm"
                                                    value={newRequirement.last_projected_year}
                                                    onChange={e => setNewRequirement({ ...newRequirement, last_projected_year: e.target.value })}
                                                />
                                            </td>
                                            <td>
                                                <button className="btn btn-sm btn-success me-2" onClick={saveNewRequirement}>Guardar</button>
                                                <button className="btn btn-sm btn-secondary" onClick={() => setCreatingRequirement(false)}>Cancelar</button>
                                            </td>
                                        </tr>
                                    )}
                                </tbody>
                            </table>
                        </div>
                        <button
                            className="btn btn-success btn-sm mb-3"
                            onClick={() => setCreatingRequirement(true)}
                            disabled={creatingRequirement}
                        >
                            Crear Necesidad
                        </button>
                    </div>
                )}
            </div>

            {/* BOTONES DE ACCIÓN */}
            <div>
                <button className="btn btn-secondary me-2" onClick={() => navigate("/projects")}>Regresar</button>
                <button className="btn btn-primary" onClick={handleSubmit}>Guardar Cambios</button>
            </div>
        </div>
    );
}

export default RequirementsGeneral;