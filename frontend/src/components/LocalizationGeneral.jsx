import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";
import { useNotification } from "../context/NotificationContext";
import entidadesCsv from "../data/entidades_territoriales.csv?raw";

function buildLocationOptions(csv) {
    const lines = csv.split("\n").slice(1).filter((l) => l.trim());
    const regionsSet = new Set();
    const departments = {};
    const cities = {};

    for (const line of lines) {
        const [region, department, city] = line.split(";").map((s) => s.trim());
        if (!region || !department) continue;
        regionsSet.add(region);
        if (!departments[region]) departments[region] = new Set();
        departments[region].add(department);
        if (city) {
            if (!cities[department]) cities[department] = new Set();
            cities[department].add(city);
        }
    }

    const regions = [...regionsSet].sort();
    const deptObj = {};
    for (const [r, s] of Object.entries(departments)) deptObj[r] = [...s].sort();
    const cityObj = {};
    for (const [d, s] of Object.entries(cities)) cityObj[d] = [...s].sort();
    return { regions, departments: deptObj, cities: cityObj };
}

const locOptions = buildLocationOptions(entidadesCsv);

function LocalizationGeneral({ projectId }) {

    const navigate = useNavigate();
    const { showSuccess, showError } = useNotification();

    const fields = [
        { key: "administrative_political_factors", label: "Aspectos administrativos y políticos" },
        { key: "proximity_to_target_population", label: "Cercanía a la población objetivo" },
        { key: "proximity_to_supply_sources", label: "Cercanía de fuentes de abastecimiento" },
        { key: "communications", label: "Comunicaciones" },
        { key: "land_cost_and_availability", label: "Costo y disponibilidad de terrenos" },
        { key: "public_services_availability", label: "Disponibilidad de servicios públicos domiciliarios" },
        { key: "labor_availability_and_cost", label: "Disponibilidad y costo de mano de obra" },
        { key: "tax_and_legal_structure", label: "Estructura impositiva y legal" },
        { key: "environmental_factors", label: "Factores ambientales" },
        { key: "gender_equity_impact", label: "Impacto para la Equidad de Género" },
        { key: "transport_means_and_costs", label: "Medios y costos de transporte" },
        { key: "public_order", label: "Orden público" },
        { key: "other_factors", label: "Otros" },
        { key: "topography", label: "Topografía" }
    ];

    const initialFormState = fields.reduce((acc, field) => {
        acc[field.key] = false;
        return acc;
    }, {});

    const emptyLocalization = {
        region: "",
        department: "",
        city: "",
        type_group: "",
        group: "",
        entity: "",
        georeferencing: true,
        latitude: "",
        longitude: ""
    };

    const [generalId, setGeneralId] = useState(null);
    const [localizations, setLocalizations] = useState([]);
    const [form, setForm] = useState(initialFormState);

    const [creating, setCreating] = useState(false);
    const [editingId, setEditingId] = useState(null);
    const [editedLoc, setEditedLoc] = useState(emptyLocalization);
    const [newLoc, setNewLoc] = useState(emptyLocalization);

    // ==========================
    // FETCH
    // ==========================

    const fetchData = async () => {
        if (!projectId) return;

        try {
            const res = await api.get(`/localization_general/project/${projectId}`);
            const data = res.data;

            setGeneralId(data.id);

            const extractedForm = {};
            fields.forEach(field => {
                extractedForm[field.key] = data[field.key] ?? false;
            });

            setForm(extractedForm);
            setLocalizations(data.localizations || []);

        } catch (error) {
            console.error(error);
        }
    };

    useEffect(() => {
        fetchData();
    }, [projectId]);

    // ==========================
    // SAVE GENERAL
    // ==========================

    const saveGeneral = async () => {
        await api.put(`/localization_general/project/${projectId}`, form);
        showSuccess("Factores guardados correctamente.");
    };

    // ==========================
    // CREATE
    // ==========================

    const saveNewLocalization = async () => {

        const payload = {
            ...newLoc,
            latitude: newLoc.georeferencing ? parseFloat(newLoc.latitude) : null,
            longitude: newLoc.georeferencing ? parseFloat(newLoc.longitude) : null,
            localization_general_id: generalId
        };

        const res = await api.post("/localization/", payload);

        setLocalizations(prev => [...prev, res.data]);
        setCreating(false);
        setNewLoc(emptyLocalization);
    };

    const handleDelete = async (id) => {
        await api.delete(`/localization/${id}`);
        setLocalizations(prev => prev.filter(l => l.id !== id));
    };

    const saveEdit = async () => {

        const payload = {
            ...editedLoc,
            latitude: editedLoc.georeferencing ? parseFloat(editedLoc.latitude) : null,
            longitude: editedLoc.georeferencing ? parseFloat(editedLoc.longitude) : null,
            localization_general_id: generalId
        };

        const res = await api.put(`/localization/${editingId}`, payload);

        setLocalizations(prev =>
            prev.map(l => l.id === editingId ? res.data : l)
        );

        setEditingId(null);
        setEditedLoc(emptyLocalization);
    };

    // ==========================
    // RENDER
    // ==========================

    return (
        <div className="container mt-4">

            <h2>Factores de Localización</h2>

            <div className="row">
                {fields.map(field => (
                    <div className="col-md-4 mb-2" key={field.key}>
                        <div className="form-check">
                            <input
                                type="checkbox"
                                className="form-check-input"
                                checked={form[field.key]}
                                onChange={(e) =>
                                    setForm({
                                        ...form,
                                        [field.key]: e.target.checked
                                    })
                                }
                            />
                            <label className="form-check-label">
                                {field.label}
                            </label>
                        </div>
                    </div>
                ))}
            </div>

            <button className="btn btn-primary mt-3" onClick={saveGeneral}>
                Guardar Factores
            </button>

            <hr />

            <h3>Registros de Localización</h3>

            <div className="table-responsive">
                <table className="table table-striped table-bordered">
                    <thead className="table-dark">
                        <tr>
                            <th>ID</th>
                            <th>Región</th>
                            <th>Departamento</th>
                            <th>Ciudad</th>
                            <th>Tipo Grupo</th>
                            <th>Grupo</th>
                            <th>Entidad</th>
                            <th>Geo</th>
                            <th>Lat</th>
                            <th>Lng</th>
                            <th>Acciones</th>
                        </tr>
                    </thead>
                    <tbody>

                        {localizations.map(loc => (
                            <tr key={loc.id}>
                                <td>{loc.id}</td>

                                {editingId === loc.id ? (
                                    <>
                                        <td>
                                            <select className="form-control" value={editedLoc.region || ""}
                                                onChange={(e) => setEditedLoc({ ...editedLoc, region: e.target.value, department: "", city: "" })}>
                                                <option value="">Seleccione región</option>
                                                {locOptions.regions.map(r => <option key={r} value={r}>{r}</option>)}
                                            </select>
                                        </td>
                                        <td>
                                            <select className="form-control" value={editedLoc.department || ""}
                                                onChange={(e) => setEditedLoc({ ...editedLoc, department: e.target.value, city: "" })}>
                                                <option value="">Seleccione departamento</option>
                                                {(locOptions.departments[editedLoc.region] || []).map(d => <option key={d} value={d}>{d}</option>)}
                                            </select>
                                        </td>
                                        <td>
                                            <select className="form-control" value={editedLoc.city || ""}
                                                onChange={(e) => setEditedLoc({ ...editedLoc, city: e.target.value })}>
                                                <option value="">Seleccione ciudad</option>
                                                {(locOptions.cities[editedLoc.department] || []).map(c => <option key={c} value={c}>{c}</option>)}
                                            </select>
                                        </td>
                                        {["type_group", "group", "entity"].map(field => (
                                            <td key={field}>
                                                <input
                                                    className="form-control"
                                                    value={editedLoc[field] || ""}
                                                    onChange={(e) =>
                                                        setEditedLoc({
                                                            ...editedLoc,
                                                            [field]: e.target.value
                                                        })
                                                    }
                                                />
                                            </td>
                                        ))}

                                        <td>
                                            <input
                                                type="checkbox"
                                                checked={editedLoc.georeferencing || false}
                                                onChange={(e) =>
                                                    setEditedLoc({
                                                        ...editedLoc,
                                                        georeferencing: e.target.checked
                                                    })
                                                }
                                            />
                                        </td>

                                        <td>
                                            <input
                                                type="number"
                                                className="form-control"
                                                value={editedLoc.latitude || ""}
                                                disabled={!editedLoc.georeferencing}
                                                onChange={(e) =>
                                                    setEditedLoc({
                                                        ...editedLoc,
                                                        latitude: e.target.value
                                                    })
                                                }
                                            />
                                        </td>

                                        <td>
                                            <input
                                                type="number"
                                                className="form-control"
                                                value={editedLoc.longitude || ""}
                                                disabled={!editedLoc.georeferencing}
                                                onChange={(e) =>
                                                    setEditedLoc({
                                                        ...editedLoc,
                                                        longitude: e.target.value
                                                    })
                                                }
                                            />
                                        </td>

                                        <td>
                                            <button className="btn btn-success btn-sm me-2" onClick={saveEdit}>Guardar</button>
                                            <button className="btn btn-secondary btn-sm" onClick={() => setEditingId(null)}>Cancelar</button>
                                        </td>
                                    </>
                                ) : (
                                    <>
                                        <td>{loc.region}</td>
                                        <td>{loc.department}</td>
                                        <td>{loc.city}</td>
                                        <td>{loc.type_group}</td>
                                        <td>{loc.group}</td>
                                        <td>{loc.entity}</td>
                                        <td>{loc.georeferencing ? "Sí" : "No"}</td>
                                        <td>{loc.latitude}</td>
                                        <td>{loc.longitude}</td>
                                        <td>
                                            <button
                                                className="btn btn-primary btn-sm me-2"
                                                onClick={() => {
                                                    setEditingId(loc.id);
                                                    setEditedLoc(loc);
                                                }}
                                            >
                                                Editar
                                            </button>
                                            <button
                                                className="btn btn-danger btn-sm"
                                                onClick={() => handleDelete(loc.id)}
                                            >
                                                Eliminar
                                            </button>
                                        </td>
                                    </>
                                )}
                            </tr>
                        ))}

                        {creating && (
                            <tr>
                                <td>Nuevo</td>

                                <td>
                                    <select className="form-control" value={newLoc.region}
                                        onChange={(e) => setNewLoc({ ...newLoc, region: e.target.value, department: "", city: "" })}>
                                        <option value="">Seleccione región</option>
                                        {locOptions.regions.map(r => <option key={r} value={r}>{r}</option>)}
                                    </select>
                                </td>
                                <td>
                                    <select className="form-control" value={newLoc.department}
                                        onChange={(e) => setNewLoc({ ...newLoc, department: e.target.value, city: "" })}>
                                        <option value="">Seleccione departamento</option>
                                        {(locOptions.departments[newLoc.region] || []).map(d => <option key={d} value={d}>{d}</option>)}
                                    </select>
                                </td>
                                <td>
                                    <select className="form-control" value={newLoc.city}
                                        onChange={(e) => setNewLoc({ ...newLoc, city: e.target.value })}>
                                        <option value="">Seleccione ciudad</option>
                                        {(locOptions.cities[newLoc.department] || []).map(c => <option key={c} value={c}>{c}</option>)}
                                    </select>
                                </td>
                                {["type_group", "group", "entity"].map(field => (
                                    <td key={field}>
                                        <input
                                            className="form-control"
                                            value={newLoc[field]}
                                            onChange={(e) =>
                                                setNewLoc({
                                                    ...newLoc,
                                                    [field]: e.target.value
                                                })
                                            }
                                        />
                                    </td>
                                ))}

                                <td>
                                    <input
                                        type="checkbox"
                                        checked={newLoc.georeferencing}
                                        onChange={(e) =>
                                            setNewLoc({
                                                ...newLoc,
                                                georeferencing: e.target.checked
                                            })
                                        }
                                    />
                                </td>

                                <td>
                                    <input
                                        type="number"
                                        className="form-control"
                                        value={newLoc.latitude}
                                        disabled={!newLoc.georeferencing}
                                        onChange={(e) =>
                                            setNewLoc({
                                                ...newLoc,
                                                latitude: e.target.value
                                            })
                                        }
                                    />
                                </td>

                                <td>
                                    <input
                                        type="number"
                                        className="form-control"
                                        value={newLoc.longitude}
                                        disabled={!newLoc.georeferencing}
                                        onChange={(e) =>
                                            setNewLoc({
                                                ...newLoc,
                                                longitude: e.target.value
                                            })
                                        }
                                    />
                                </td>

                                <td>
                                    <button className="btn btn-success btn-sm me-2" onClick={saveNewLocalization}>Guardar</button>
                                    <button className="btn btn-secondary btn-sm" onClick={() => setCreating(false)}>Cancelar</button>
                                </td>
                            </tr>
                        )}

                    </tbody>
                </table>
            </div>

            <button
                className="btn btn-success btn-sm mb-3"
                onClick={() => setCreating(true)}
                disabled={!generalId}
            >
                Crear Registro
            </button>

            <div className="mt-4">
                <button
                    className="btn btn-secondary"
                    onClick={() => navigate("/projects")}
                >
                    Regresar
                </button>
            </div>

        </div>
    );
}

export default LocalizationGeneral;