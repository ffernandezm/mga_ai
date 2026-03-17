import { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../services/api";
import "../styles/ProjectForm.css";

function CreateProject() {
    const { id } = useParams();
    const navigate = useNavigate();

    // Estado inicial con todos los nuevos campos
    const [project, setProject] = useState({
        name: "",
        description: "",
        process: "",
        object_desc: "",
        region: "",
        department: "",
        municipality: "",
        intervention_type: "",
        project_typology: "",
        main_product: "",
        sector: ""
    });

    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (id) {
            const fetchProject = async () => {
                try {
                    const response = await api.get(`/projects/${id}`);
                    setProject(response.data);
                } catch (error) {
                    console.error("Error fetching project:", error);
                }
            };
            fetchProject();
        }
    }, [id]);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setProject((prev) => ({
            ...prev,
            [name]: value
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!project.name.trim()) return;

        setLoading(true);
        try {
            if (id) {
                await api.put(`/projects/${id}`, project);
            } else {
                await api.post("/projects/", project);
            }
            navigate("/projects");
        } catch (error) {
            console.error("Error saving project", error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="project-container">
            <header className="form-header">
                <h2>{id ? "Editar Proyecto" : "Nuevo Proyecto MGA"}</h2>
                <p>Complete la información técnica para la formulación del proyecto.</p>
            </header>

            <form onSubmit={handleSubmit} className="project-form">

                {/* SECCIÓN 1: IDENTIFICACIÓN GENERAL */}
                <section className="form-section">
                    <h3>Identificación General</h3>
                    <div className="form-grid">
                        <div className="form-group full-width">
                            <label>Nombre del Proyecto *</label>
                            <input
                                type="text"
                                name="name"
                                value={project.name}
                                onChange={handleChange}
                                placeholder="Ej: Fortalecimiento de la infraestructura..."
                                required
                            />
                        </div>
                        <div className="form-group">
                            <label>Proceso</label>
                            <input type="text" name="process" value={project.process} onChange={handleChange} />
                        </div>
                        <div className="form-group">
                            <label>Sector</label>
                            <input type="text" name="sector" value={project.sector} onChange={handleChange} />
                        </div>
                        <div className="form-group full-width">
                            <label>Objeto</label>
                            <textarea name="object_desc" value={project.object_desc} onChange={handleChange} rows="2" />
                        </div>
                    </div>
                </section>

                {/* SECCIÓN 2: LOCALIZACIÓN */}
                <section className="form-section">
                    <h3>Localización Geográfica</h3>
                    <div className="form-grid">
                        <div className="form-group">
                            <label>Región</label>
                            <input type="text" name="region" value={project.region} onChange={handleChange} />
                        </div>
                        <div className="form-group">
                            <label>Departamento</label>
                            <input type="text" name="department" value={project.department} onChange={handleChange} />
                        </div>
                        <div className="form-group">
                            <label>Municipio</label>
                            <input type="text" name="municipality" value={project.municipality} onChange={handleChange} />
                        </div>
                    </div>
                </section>

                {/* SECCIÓN 3: CLASIFICACIÓN TÉCNICA */}
                <section className="form-section">
                    <h3>Clasificación y Tipología</h3>
                    <div className="form-grid">
                        <div className="form-group">
                            <label>Tipo de Intervención</label>
                            <input type="text" name="intervention_type" value={project.intervention_type} onChange={handleChange} />
                        </div>
                        <div className="form-group">
                            <label>Tipología de Proyecto</label>
                            <input type="text" name="project_typology" value={project.project_typology} onChange={handleChange} />
                        </div>
                        <div className="form-group full-width">
                            <label>Producto Principal</label>
                            <input type="text" name="main_product" value={project.main_product} onChange={handleChange} />
                        </div>
                        <div className="form-group full-width">
                            <label>Descripción General</label>
                            <textarea name="description" value={project.description} onChange={handleChange} rows="3" />
                        </div>
                    </div>
                </section>

                <div className="form-actions">
                    <button type="submit" className="btn-primary" disabled={loading}>
                        {loading ? "Guardando..." : id ? "Actualizar Proyecto" : "Crear Proyecto"}
                    </button>
                    <button type="button" className="btn-secondary" onClick={() => navigate("/projects")}>
                        Cancelar
                    </button>
                </div>
            </form>
        </div>
    );
}

export default CreateProject;