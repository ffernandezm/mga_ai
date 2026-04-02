import { useState, useEffect, useMemo } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../services/api";
import processCsv from "../data/proceso.csv?raw";
import territorialEntitiesCsv from "../data/entidades_territoriales.csv?raw";
import investmentTypologyCsv from "../data/inversion_tipologia.csv?raw";
import ProductCatalogWizard from "../components/ProductCatalogWizard";
import { useNotification } from "../context/NotificationContext";
import "../styles/ProjectForm.css";

function CreateProject() {
    const { id } = useParams();
    const navigate = useNavigate();
    const { showSuccess, showError } = useNotification();

    // Estado del proyecto (sin region/department/municipality)
    const [project, setProject] = useState({
        name: "",
        description: "",
        process: "",
        object_desc: "",
        intervention_type: "",
        project_typology: "",
        main_product: "",
        sector: "",
        indicator_code: ""
    });

    // Localizaciones múltiples
    const [localizations, setLocalizations] = useState([]);
    const [newLocalization, setNewLocalization] = useState({
        region: "",
        department: "",
        municipality: ""
    });

    const [loading, setLoading] = useState(false);
    const [processOptions, setProcessOptions] = useState([]);
    const [loadingProcess, setLoadingProcess] = useState(true);
    const [territorialEntities, setTerritorialEntities] = useState([]);
    const [loadingTerritorialEntities, setLoadingTerritorialEntities] = useState(true);
    const [investmentTypologies, setInvestmentTypologies] = useState([]);
    const [loadingInvestmentTypologies, setLoadingInvestmentTypologies] = useState(true);
    const [showCatalogWizard, setShowCatalogWizard] = useState(false);

    // --- Computed options para el formulario de nueva localización ---
    const regionOptions = useMemo(() => {
        const uniqueRegions = [...new Set(territorialEntities.map(item => item.region))];
        return uniqueRegions.sort((a, b) => a.localeCompare(b, "es"));
    }, [territorialEntities]);

    const departmentOptions = useMemo(() => {
        if (!newLocalization.region) return [];
        const uniqueDepartments = [
            ...new Set(
                territorialEntities
                    .filter(item => item.region === newLocalization.region)
                    .map(item => item.department)
            )
        ];
        return uniqueDepartments.sort((a, b) => a.localeCompare(b, "es"));
    }, [territorialEntities, newLocalization.region]);

    const municipalityOptions = useMemo(() => {
        if (!newLocalization.region || !newLocalization.department) return [];
        const uniqueMunicipalities = [
            ...new Set(
                territorialEntities
                    .filter(
                        item =>
                            item.region === newLocalization.region &&
                            item.department === newLocalization.department
                    )
                    .map(item => item.municipality)
            )
        ];
        return uniqueMunicipalities.sort((a, b) => a.localeCompare(b, "es"));
    }, [territorialEntities, newLocalization.region, newLocalization.department]);

    const interventionTypeOptions = useMemo(() => {
        const uniqueInterventionTypes = [
            ...new Set(investmentTypologies.map(item => item.interventionType))
        ];

        return uniqueInterventionTypes.sort((a, b) => a.localeCompare(b, "es"));
    }, [investmentTypologies]);

    const projectTypologyOptions = useMemo(() => {
        if (!project.intervention_type) return [];

        const uniqueProjectTypologies = [
            ...new Set(
                investmentTypologies
                    .filter(
                        item => item.interventionType === project.intervention_type
                    )
                    .map(item => item.projectTypology)
            )
        ];

        return uniqueProjectTypologies.sort((a, b) => a.localeCompare(b, "es"));
    }, [investmentTypologies, project.intervention_type]);

    // Cargar opciones del CSV al montar el componente
    useEffect(() => {
        const fetchProcessOptions = () => {
            try {
                const csvText = processCsv;

                // Parsear CSV (una sola columna, sin comas en los valores)
                const lines = csvText.split(/\r?\n/).filter(line => line.trim() !== "");
                if (lines.length > 0) {
                    // La primera línea es el encabezado "PProceso"
                    const options = lines.slice(1).map(line => line.trim());
                    setProcessOptions(options);
                } else {
                    setProcessOptions([]);
                }
            } catch (error) {
                console.error("Error cargando proceso.csv:", error);
                setProcessOptions([]);
            } finally {
                setLoadingProcess(false);
            }
        };

        fetchProcessOptions();
    }, []);

    useEffect(() => {
        const fetchTerritorialEntities = () => {
            try {
                const lines = territorialEntitiesCsv
                    .split(/\r?\n/)
                    .filter(line => line.trim() !== "");

                if (lines.length <= 1) {
                    setTerritorialEntities([]);
                    return;
                }

                const options = lines
                    .slice(1)
                    .map(line => {
                        const [region, department, municipality] = line
                            .split(";")
                            .map(value => value.trim());

                        return { region, department, municipality };
                    })
                    .filter(
                        item => item.region && item.department && item.municipality
                    );

                setTerritorialEntities(options);
            } catch (error) {
                console.error("Error cargando entidades_territoriales.csv:", error);
                setTerritorialEntities([]);
            } finally {
                setLoadingTerritorialEntities(false);
            }
        };

        fetchTerritorialEntities();
    }, []);

    useEffect(() => {
        const fetchInvestmentTypologies = () => {
            try {
                const lines = investmentTypologyCsv
                    .split(/\r?\n/)
                    .filter(line => line.trim() !== "");

                if (lines.length <= 1) {
                    setInvestmentTypologies([]);
                    return;
                }

                const options = lines
                    .slice(1)
                    .map(line => {
                        const [interventionType, projectTypology] = line
                            .split(",")
                            .map(value => value.trim());

                        return { interventionType, projectTypology };
                    })
                    .filter(
                        item => item.interventionType && item.projectTypology
                    );

                setInvestmentTypologies(options);
            } catch (error) {
                console.error("Error cargando inversion_tipologia.csv:", error);
                setInvestmentTypologies([]);
            } finally {
                setLoadingInvestmentTypologies(false);
            }
        };

        fetchInvestmentTypologies();
    }, []);

    // Cargar proyecto y localizaciones si estamos en edición
    useEffect(() => {
        if (id) {
            const fetchProject = async () => {
                try {
                    const [projectRes, locRes] = await Promise.all([
                        api.get(`/projects/${id}`),
                        api.get(`/project_localizations/project/${id}`)
                    ]);
                    setProject(projectRes.data);
                    setLocalizations(locRes.data);
                } catch (error) {
                    console.error("Error fetching project:", error);
                }
            };
            fetchProject();
        }
    }, [id]);

    const handleChange = (e) => {
        const { name, value } = e.target;

        if (name === "intervention_type") {
            setProject(prev => ({
                ...prev,
                intervention_type: value,
                project_typology: ""
            }));
            return;
        }

        setProject((prev) => ({
            ...prev,
            [name]: value
        }));
    };

    // --- Manejo de localizaciones ---
    const handleLocalizationChange = (e) => {
        const { name, value } = e.target;

        if (name === "region") {
            setNewLocalization({ region: value, department: "", municipality: "" });
            return;
        }
        if (name === "department") {
            setNewLocalization(prev => ({ ...prev, department: value, municipality: "" }));
            return;
        }
        setNewLocalization(prev => ({ ...prev, [name]: value }));
    };

    const handleAddLocalization = () => {
        if (!newLocalization.region || !newLocalization.department || !newLocalization.municipality) return;

        const exists = localizations.some(
            loc =>
                loc.region === newLocalization.region &&
                loc.department === newLocalization.department &&
                loc.municipality === newLocalization.municipality
        );
        if (exists) return;

        setLocalizations(prev => [...prev, { ...newLocalization, _temp: true }]);
        setNewLocalization({ region: "", department: "", municipality: "" });
    };

    const handleRemoveLocalization = (index) => {
        setLocalizations(prev => prev.filter((_, i) => i !== index));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!project.name.trim()) return;

        setLoading(true);
        try {
            let projectId = id;

            if (id) {
                await api.put(`/projects/${id}`, project);
                // Eliminar localizaciones anteriores y crear las nuevas
                await api.delete(`/project_localizations/project/${id}`);
            } else {
                const res = await api.post("/projects/", project);
                projectId = res.data.id;
            }

            // Crear todas las localizaciones
            await Promise.all(
                localizations.map(loc =>
                    api.post("/project_localizations/", {
                        project_id: projectId,
                        region: loc.region,
                        department: loc.department,
                        municipality: loc.municipality,
                    })
                )
            );

            navigate("/projects");
        } catch (error) {
            console.error("Error saving project", error);
            showError("Error al guardar el proyecto.");
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
                            {loadingProcess ? (
                                <input type="text" disabled value="Cargando opciones..." />
                            ) : (
                                <select
                                    name="process"
                                    value={project.process}
                                    onChange={handleChange}
                                >
                                    <option value="">Seleccione</option>
                                    {processOptions.map((opt, idx) => (
                                        <option key={idx} value={opt}>
                                            {opt}
                                        </option>
                                    ))}
                                </select>
                            )}
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

                    {/* Formulario para agregar nueva localización */}
                    <div className="loc-add-row">
                        <div className="loc-field">
                            <label>Región</label>
                            {loadingTerritorialEntities ? (
                                <input type="text" disabled value="Cargando..." />
                            ) : (
                                <select
                                    name="region"
                                    value={newLocalization.region}
                                    onChange={handleLocalizationChange}
                                >
                                    <option value="">Seleccione</option>
                                    {regionOptions.map((opt, idx) => (
                                        <option key={idx} value={opt}>{opt}</option>
                                    ))}
                                </select>
                            )}
                        </div>
                        <div className="loc-field">
                            <label>Departamento</label>
                            {loadingTerritorialEntities ? (
                                <input type="text" disabled value="Cargando..." />
                            ) : (
                                <select
                                    name="department"
                                    value={newLocalization.department}
                                    onChange={handleLocalizationChange}
                                    disabled={!newLocalization.region}
                                >
                                    <option value="">Seleccione</option>
                                    {departmentOptions.map((opt, idx) => (
                                        <option key={idx} value={opt}>{opt}</option>
                                    ))}
                                </select>
                            )}
                        </div>
                        <div className="loc-field">
                            <label>Municipio</label>
                            {loadingTerritorialEntities ? (
                                <input type="text" disabled value="Cargando..." />
                            ) : (
                                <select
                                    name="municipality"
                                    value={newLocalization.municipality}
                                    onChange={handleLocalizationChange}
                                    disabled={!newLocalization.region || !newLocalization.department}
                                >
                                    <option value="">Seleccione</option>
                                    {municipalityOptions.map((opt, idx) => (
                                        <option key={idx} value={opt}>{opt}</option>
                                    ))}
                                </select>
                            )}
                        </div>
                        <button
                            type="button"
                            className="btn-add-loc"
                            onClick={handleAddLocalization}
                            disabled={!newLocalization.region || !newLocalization.department || !newLocalization.municipality}
                        >
                            + Agregar
                        </button>
                    </div>

                    {/* Tabla de localizaciones */}
                    {localizations.length > 0 && (
                        <div className="loc-table-container">
                            <table className="loc-table">
                                <thead>
                                    <tr>
                                        <th>#</th>
                                        <th>Región</th>
                                        <th>Departamento</th>
                                        <th>Municipio</th>
                                        <th>Acciones</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {localizations.map((loc, idx) => (
                                        <tr key={loc.id || `temp-${idx}`}>
                                            <td>{idx + 1}</td>
                                            <td>{loc.region}</td>
                                            <td>{loc.department}</td>
                                            <td>{loc.municipality}</td>
                                            <td>
                                                <button
                                                    type="button"
                                                    className="btn-remove-loc"
                                                    onClick={() => handleRemoveLocalization(idx)}
                                                    title="Eliminar"
                                                >
                                                    ✕
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </section>

                {/* SECCIÓN 3: CLASIFICACIÓN TÉCNICA */}
                <section className="form-section">
                    <h3>Clasificación y Tipología</h3>
                    <div className="form-grid">
                        <div className="form-group">
                            <label>Tipo de Intervención</label>
                            {loadingInvestmentTypologies ? (
                                <input type="text" disabled value="Cargando opciones..." />
                            ) : (
                                <select
                                    name="intervention_type"
                                    value={project.intervention_type}
                                    onChange={handleChange}
                                >
                                    <option value="">Seleccione</option>
                                    {interventionTypeOptions.map((opt, idx) => (
                                        <option key={idx} value={opt}>
                                            {opt}
                                        </option>
                                    ))}
                                </select>
                            )}
                        </div>
                        <div className="form-group">
                            <label>Tipología de Proyecto</label>
                            {loadingInvestmentTypologies ? (
                                <input type="text" disabled value="Cargando opciones..." />
                            ) : (
                                <select
                                    name="project_typology"
                                    value={project.project_typology}
                                    onChange={handleChange}
                                    disabled={!project.intervention_type}
                                >
                                    <option value="">Seleccione</option>
                                    {projectTypologyOptions.map((opt, idx) => (
                                        <option key={idx} value={opt}>
                                            {opt}
                                        </option>
                                    ))}
                                </select>
                            )}
                        </div>
                        <div className="form-group full-width">
                            <label>Producto Principal</label>
                            <input type="text" name="main_product" value={project.main_product} onChange={handleChange} />
                            <button
                                type="button"
                                className="btn-catalog"
                                onClick={() => setShowCatalogWizard(true)}
                            >
                                Buscar en Catálogo de Productos
                            </button>
                        </div>
                        <input type="hidden" name="indicator_code" value={project.indicator_code} />
                        <div className="form-group">
                            <label>Sector</label>
                            <input type="text" name="sector" value={project.sector} onChange={handleChange} />
                        </div>
                        <div className="form-group full-width">
                            <label>Descripción General</label>
                            <textarea name="description" value={project.description} onChange={handleChange} rows="3" />
                        </div>
                    </div>
                </section>

                <div className="form-actions">
                    <button type="submit" className="btn-submit" disabled={loading}>
                        {loading ? "Guardando..." : id ? "Actualizar Proyecto" : "Crear Proyecto"}
                    </button>
                    <button type="button" className="btn-cancel" onClick={() => navigate("/projects")}>
                        Cancelar
                    </button>
                </div>
            </form>

            <ProductCatalogWizard
                isOpen={showCatalogWizard}
                onClose={() => setShowCatalogWizard(false)}
                onSelect={({ main_product, sector, indicator_code }) => {
                    setProject(prev => ({ ...prev, main_product, sector, indicator_code }));
                }}
            />
        </div>
    );
}

export default CreateProject;