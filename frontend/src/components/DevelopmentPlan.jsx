import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

function DevelopmentPlan({ projectId }) {
    const navigate = useNavigate();

    // Estado para saber si ya existe el registro (PUT) o es nuevo (POST)
    const [planId, setPlanId] = useState(null);

    // Estado centralizado para todos los campos del formulario
    const [formData, setFormData] = useState({
        program: "",
        national_development_plan: "",
        departmental_or_sectoral_development_plan: "",
        strategy_departmental: "",
        program_departmental: "",
        district_or_municipal_development_plan: "",
        strategy_district: "",
        program_district: "",
        community_type: "",
        ethnic_group_planning_instruments: "",
        other_development_plan: "",
        strategy_other: "",
        program_other: "",
        pnds: [], // <-- Añadimos el array para manejar la tabla de PND
    });

    // Estado para controlar qué sección está desplegada
    const [expandedSections, setExpandedSections] = useState({
        national: true, // La primera abierta por defecto
        departmental: false,
        district: false,
        ethnic: false,
        other: false
    });

    // ---------- FETCH ----------
    const fetchDevelopmentPlan = async () => {
        try {
            const res = await api.get(`/development_plans/${projectId}`);
            if (res.data) {
                setPlanId(res.data.id);

                // Reemplazamos los nulls por strings vacíos para evitar warnings de React
                const sanitizedData = {};
                for (const key in res.data) {
                    if (key === 'pnds') {
                        // Nos aseguramos de que sea un array
                        sanitizedData[key] = res.data[key] || [];
                    } else {
                        sanitizedData[key] = res.data[key] === null ? "" : res.data[key];
                    }
                }
                setFormData(sanitizedData);
            }
        } catch (error) {
            // Si es 404, simplemente significa que no se ha creado aún, no es un error crítico
            if (error.response?.status !== 404) {
                console.error("Error cargando el plan de desarrollo:", error);
            }
        }
    };

    useEffect(() => {
        if (projectId) {
            fetchDevelopmentPlan();
        }
    }, [projectId]);

    // ---------- HANDLERS GENERALES ----------
    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({
            ...prev,
            [name]: value
        }));
    };

    const toggleSection = (section) => {
        setExpandedSections((prev) => ({
            ...prev,
            [section]: !prev[section]
        }));
    };

    // ---------- HANDLERS PARA TABLA PND ----------
    const handlePndChange = (index, field, value) => {
        const newPnds = [...formData.pnds];
        newPnds[index][field] = value;
        setFormData((prev) => ({ ...prev, pnds: newPnds }));
    };

    const addPndRow = () => {
        setFormData((prev) => ({
            ...prev,
            pnds: [
                ...prev.pnds,
                { transformation: "", pillar: "", catalyst: "", component: "" }
            ]
        }));
    };

    const removePndRow = (index) => {
        const newPnds = formData.pnds.filter((_, i) => i !== index);
        setFormData((prev) => ({ ...prev, pnds: newPnds }));
    };

    // ---------- GUARDAR ----------
    const handleSubmit = async () => {
        const payload = {
            ...formData,
            project_id: projectId // Importante enviar el ID del proyecto asociado
        };

        try {
            if (planId) {
                // Actualizar (PUT)
                await api.put(`/development_plans/${projectId}`, payload);
            } else {
                // Crear (POST)
                const res = await api.post(`/development_plans/`, payload);
                setPlanId(res.data.id);
            }
            alert("Plan de desarrollo guardado exitosamente");
        } catch (err) {
            console.error(err);
            alert("Error al guardar el plan de desarrollo");
        }
    };

    // ---------- RENDER DE SECCIONES DESPLEGABLES ----------
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

    return (
        <div className="container mt-4 mb-5">
            <h2 className="mb-4">Plan de Desarrollo</h2>

            {/* ---------- SECCIÓN 1: Plan Nacional ---------- */}
            <div className="card mb-3 shadow-sm">
                {renderSectionHeader("national", "Contribución al Plan Nacional de Desarrollo")}
                {expandedSections.national && (
                    <div className="card-body row g-3">
                        <div className="col-md-6">
                            <label className="form-label">Programa</label>
                            <input type="text" className="form-control" name="program" value={formData.program} onChange={handleChange} />
                        </div>
                        <div className="col-md-6">
                            <label className="form-label">Plan Nacional de Desarrollo</label>
                            <input type="text" className="form-control" name="national_development_plan" value={formData.national_development_plan} onChange={handleChange} />
                        </div>

                        {/* TABLA DINÁMICA DE PND */}
                        <div className="col-12 mt-4">
                            <h6 className="mb-3">Detalle PND</h6>
                            <div className="table-responsive">
                                <table className="table table-bordered table-sm">
                                    <thead className="table-light">
                                        <tr>
                                            <th>Transformación</th>
                                            <th>Pilar</th>
                                            <th>Catalizador</th>
                                            <th>Componente</th>
                                            <th style={{ width: "80px" }}>Acciones</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {formData.pnds.map((pnd, index) => (
                                            <tr key={index}>
                                                <td>
                                                    <input type="text" className="form-control form-control-sm" value={pnd.transformation} onChange={(e) => handlePndChange(index, "transformation", e.target.value)} />
                                                </td>
                                                <td>
                                                    <input type="text" className="form-control form-control-sm" value={pnd.pillar} onChange={(e) => handlePndChange(index, "pillar", e.target.value)} />
                                                </td>
                                                <td>
                                                    <input type="text" className="form-control form-control-sm" value={pnd.catalyst} onChange={(e) => handlePndChange(index, "catalyst", e.target.value)} />
                                                </td>
                                                <td>
                                                    <input type="text" className="form-control form-control-sm" value={pnd.component} onChange={(e) => handlePndChange(index, "component", e.target.value)} />
                                                </td>
                                                <td className="text-center">
                                                    <button type="button" className="btn btn-danger btn-sm" onClick={() => removePndRow(index)}>
                                                        X
                                                    </button>
                                                </td>
                                            </tr>
                                        ))}
                                        {formData.pnds.length === 0 && (
                                            <tr>
                                                <td colSpan="5" className="text-center text-muted">No hay registros asociados.</td>
                                            </tr>
                                        )}
                                    </tbody>
                                </table>
                            </div>
                            <button type="button" className="btn btn-outline-primary btn-sm" onClick={addPndRow}>
                                + Agregar Fila
                            </button>
                        </div>
                    </div>
                )}
            </div>

            {/* ---------- SECCIÓN 2: Plan Departamental o Sectorial ---------- */}
            <div className="card mb-3 shadow-sm">
                {renderSectionHeader("departmental", "Plan de Desarrollo Departamental o Sectorial")}
                {expandedSections.departmental && (
                    <div className="card-body row g-3">
                        <div className="col-12">
                            <label className="form-label">Plan de Desarrollo Departamental / Sectorial</label>
                            <input type="text" className="form-control" name="departmental_or_sectoral_development_plan" value={formData.departmental_or_sectoral_development_plan} onChange={handleChange} />
                        </div>
                        <div className="col-md-6">
                            <label className="form-label">Estrategia Departamental</label>
                            <input type="text" className="form-control" name="strategy_departmental" value={formData.strategy_departmental} onChange={handleChange} />
                        </div>
                        <div className="col-md-6">
                            <label className="form-label">Programa Departamental</label>
                            <input type="text" className="form-control" name="program_departmental" value={formData.program_departmental} onChange={handleChange} />
                        </div>
                    </div>
                )}
            </div>

            {/* ---------- SECCIÓN 3: Plan Distrital o Municipal ---------- */}
            <div className="card mb-3 shadow-sm">
                {renderSectionHeader("district", "Plan de Desarrollo Distrital o Municipal")}
                {expandedSections.district && (
                    <div className="card-body row g-3">
                        <div className="col-12">
                            <label className="form-label">Plan de Desarrollo Distrital / Municipal</label>
                            <input type="text" className="form-control" name="district_or_municipal_development_plan" value={formData.district_or_municipal_development_plan} onChange={handleChange} />
                        </div>
                        <div className="col-md-6">
                            <label className="form-label">Estrategia Distrital</label>
                            <input type="text" className="form-control" name="strategy_district" value={formData.strategy_district} onChange={handleChange} />
                        </div>
                        <div className="col-md-6">
                            <label className="form-label">Programa Distrital</label>
                            <input type="text" className="form-control" name="program_district" value={formData.program_district} onChange={handleChange} />
                        </div>
                    </div>
                )}
            </div>

            {/* ---------- SECCIÓN 4: Grupos Étnicos ---------- */}
            <div className="card mb-3 shadow-sm">
                {renderSectionHeader("ethnic", "Instrumentos de Planeación de Grupos Étnicos")}
                {expandedSections.ethnic && (
                    <div className="card-body row g-3">
                        <div className="col-md-6">
                            <label className="form-label">Tipo de Comunidad</label>
                            <input type="text" className="form-control" name="community_type" value={formData.community_type} onChange={handleChange} />
                        </div>
                        <div className="col-md-6">
                            <label className="form-label">Instrumentos de Planeación (Grupos Étnicos)</label>
                            <input type="text" className="form-control" name="ethnic_group_planning_instruments" value={formData.ethnic_group_planning_instruments} onChange={handleChange} />
                        </div>
                    </div>
                )}
            </div>

            {/* ---------- SECCIÓN 5: Otros Instrumentos ---------- */}
            <div className="card mb-3 shadow-sm">
                {renderSectionHeader("other", "Otros Instrumentos de Planeación")}
                {expandedSections.other && (
                    <div className="card-body row g-3">
                        <div className="col-12">
                            <label className="form-label">Otro Plan de Desarrollo</label>
                            <input type="text" className="form-control" name="other_development_plan" value={formData.other_development_plan} onChange={handleChange} />
                        </div>
                        <div className="col-md-6">
                            <label className="form-label">Estrategia (Otro)</label>
                            <input type="text" className="form-control" name="strategy_other" value={formData.strategy_other} onChange={handleChange} />
                        </div>
                        <div className="col-md-6">
                            <label className="form-label">Programa (Otro)</label>
                            <input type="text" className="form-control" name="program_other" value={formData.program_other} onChange={handleChange} />
                        </div>
                    </div>
                )}
            </div>

            {/* ---------- BOTONES DE ACCIÓN ---------- */}
            <div className="d-flex justify-content-end mt-4">
                <button
                    className="btn btn-secondary me-2"
                    onClick={() => navigate("/projects")}
                >
                    Regresar
                </button>
                <button
                    className="btn btn-primary"
                    onClick={handleSubmit}
                >
                    Guardar Cambios
                </button>
            </div>
        </div>
    );
}

export default DevelopmentPlan;