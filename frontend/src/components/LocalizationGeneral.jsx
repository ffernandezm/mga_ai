import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

function LocalizationGeneral({ projectId }) {

    const navigate = useNavigate();

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
        alert("Saved");
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

            <h2>Localization Factors</h2>

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
                Save Factors
            </button>

            <hr />

            <h3>Localization Records</h3>

            <table className="table table-bordered">
                <thead className="table-dark">
                    <tr>
                        <th>ID</th>
                        <th>Region</th>
                        <th>Department</th>
                        <th>City</th>
                        <th>Type Group</th>
                        <th>Group</th>
                        <th>Entity</th>
                        <th>Geo</th>
                        <th>Lat</th>
                        <th>Lng</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>

                    {localizations.map(loc => (
                        <tr key={loc.id}>
                            <td>{loc.id}</td>

                            {editingId === loc.id ? (
                                <>
                                    {["region", "department", "city", "type_group", "group", "entity"].map(field => (
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
                                        <button className="btn btn-success btn-sm me-2" onClick={saveEdit}>Save</button>
                                        <button className="btn btn-secondary btn-sm" onClick={() => setEditingId(null)}>Cancel</button>
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
                                    <td>{loc.georeferencing ? "Yes" : "No"}</td>
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
                                            Edit
                                        </button>
                                        <button
                                            className="btn btn-danger btn-sm"
                                            onClick={() => handleDelete(loc.id)}
                                        >
                                            Delete
                                        </button>
                                    </td>
                                </>
                            )}
                        </tr>
                    ))}

                    {creating && (
                        <tr>
                            <td>New</td>

                            {["region", "department", "city", "type_group", "group", "entity"].map(field => (
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
                                <button className="btn btn-success btn-sm me-2" onClick={saveNewLocalization}>Save</button>
                                <button className="btn btn-secondary btn-sm" onClick={() => setCreating(false)}>Cancel</button>
                            </td>
                        </tr>
                    )}

                </tbody>
            </table>

            <button
                className="btn btn-success"
                onClick={() => setCreating(true)}
                disabled={!generalId}
            >
                Add Record
            </button>

            <div className="mt-4">
                <button
                    className="btn btn-secondary"
                    onClick={() => navigate("/projects")}
                >
                    Back
                </button>
            </div>

        </div>
    );
}

export default LocalizationGeneral;