import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";
import populationOptions from "../data/populationOptions";

function Population({ projectId }) {
    const [affectedPopulation, setAffectedPopulation] = useState([]);
    const [interventionPopulation, setInterventionPopulation] = useState([]);
    const [characteristicsPopulation, setCharacteristicsPopulation] = useState([]);
    const [analysis, setAnalysis] = useState("");
    const [populationId, setPopulationId] = useState(null);

    // Estados de edición
    const [editingAffectedId, setEditingAffectedId] = useState(null);
    const [editingInterventionId, setEditingInterventionId] = useState(null);
    const [editingCharacteristicId, setEditingCharacteristicId] = useState(null);
    const [editedAffected, setEditedAffected] = useState({});
    const [editedIntervention, setEditedIntervention] = useState({});
    const [editedCharacteristic, setEditedCharacteristic] = useState({});

    // Estados de creación inline
    const [creatingAffected, setCreatingAffected] = useState(false);
    const [creatingIntervention, setCreatingIntervention] = useState(false);
    const [newAffected, setNewAffected] = useState({
        region: "",
        department: "",
        city: "",
        population_center: "",
        location_entity: "",
    });
    const [newIntervention, setNewIntervention] = useState({
        region: "",
        department: "",
        city: "",
        population_center: "",
        location_entity: "",
    });

    const navigate = useNavigate();
    const { regions, departments, cities, populationCenters, locationEntities } = populationOptions;

    const fetchPopulation = async () => {
        try {
            const response = await api.get(`/population/${projectId}`);
            const data = response.data;
            if (data) {
                setAnalysis(data.population_json?.analysis || "");
                setPopulationId(data.id);
                setAffectedPopulation(data.affected_population || []);
                setInterventionPopulation(data.intervention_population || []);
                setCharacteristicsPopulation(data.characteristics_population || []);
            } else {
                // Inicializar vacíos si no existe
                setAffectedPopulation([]);
                setInterventionPopulation([]);
                setCharacteristicsPopulation([]);
                setPopulationId(null);
                setAnalysis("");
            }
        } catch (error) {
            console.error("Error al obtener la Población:", error);
        }
    };

    useEffect(() => {
        if (projectId) fetchPopulation();
    }, [projectId]);

    const handleSubmit = async () => {
        if (!projectId) return alert("No hay proyecto seleccionado.");

        const payload = {
            project_id: projectId,
            population_json: { analysis },
            affected_population: affectedPopulation,
            intervention_population: interventionPopulation,
            characteristics_population: characteristicsPopulation,
        };

        try {
            if (populationId) {
                await api.put(`/population/${populationId}`, payload);
            } else {
                const res = await api.post(`/population`, payload);
                setPopulationId(res.data.id);
            }
            alert("Población actualizada correctamente.");
            fetchPopulation();
        } catch (err) {
            console.error("Error al guardar la información:", err);
            alert("Error al guardar la información.");
        }
    };

    const handleDelete = async (id, type) => {
        if (!id) return;
        if (window.confirm("¿Eliminar este registro?")) {
            try {
                const endpoint =
                    type === "affected"
                        ? `/affected_population/${id}`
                        : type === "intervention"
                            ? `/intervention_population/${id}`
                            : `/characteristics_population/${id}`;

                await api.delete(endpoint);

                if (type === "affected") {
                    setAffectedPopulation(prev => prev.filter(item => item.id !== id));
                } else if (type === "intervention") {
                    setInterventionPopulation(prev => prev.filter(item => item.id !== id));
                } else {
                    setCharacteristicsPopulation(prev => prev.filter(item => item.id !== id));
                }
            } catch (error) {
                console.error("Error al eliminar registro:", error);
                alert("Error al eliminar registro.");
            }
        }
    };

    // ---------- EDICIÓN EN LÍNEA (restaurada) ----------
    const handleEditAffected = (affected) => {
        setEditingAffectedId(affected.id);
        setEditedAffected({ ...affected });
    };

    const handleEditIntervention = (intervention) => {
        setEditingInterventionId(intervention.id);
        setEditedIntervention({ ...intervention });
    };

    const handleEditCharacteristic = (characteristic) => {
        setEditingCharacteristicId(characteristic.id);
        setEditedCharacteristic({ ...characteristic });
    };

    const handleAffectedChange = (field, value) => {
        setEditedAffected(prev => ({
            ...prev,
            [field]: value,
            ...(field === "region" && { department: "", city: "" }),
            ...(field === "department" && { city: "" })
        }));
    };

    const handleInterventionChange = (field, value) => {
        setEditedIntervention(prev => ({
            ...prev,
            [field]: value,
            ...(field === "region" && { department: "", city: "" }),
            ...(field === "department" && { city: "" })
        }));
    };

    const handleCharacteristicChange = (field, value) => {
        setEditedCharacteristic(prev => ({
            ...prev,
            [field]: field === 'people_number' ? parseInt(value) || 0 : value
        }));
    };

    const handleSaveAffected = async () => {
        try {
            await api.put(`/affected_population/${editingAffectedId}`, editedAffected);

            setAffectedPopulation(prev =>
                prev.map(affected =>
                    affected.id === editingAffectedId ? { ...editedAffected } : affected
                )
            );

            setEditingAffectedId(null);
            setEditedAffected({});
            alert("Población afectada actualizada correctamente.");
        } catch (error) {
            console.error("Error al actualizar población afectada:", error);
            alert("Error al actualizar población afectada.");
        }
    };

    const handleSaveIntervention = async () => {
        try {
            await api.put(`/intervention_population/${editingInterventionId}`, editedIntervention);

            setInterventionPopulation(prev =>
                prev.map(intervention =>
                    intervention.id === editingInterventionId ? { ...editedIntervention } : intervention
                )
            );

            setEditingInterventionId(null);
            setEditedIntervention({});
            alert("Población de intervención actualizada correctamente.");
        } catch (error) {
            console.error("Error al actualizar población de intervención:", error);
            alert("Error al actualizar población de intervención.");
        }
    };

    const handleSaveCharacteristic = async () => {
        try {
            await api.put(`/characteristics_population/${editingCharacteristicId}`, editedCharacteristic);

            setCharacteristicsPopulation(prev =>
                prev.map(characteristic =>
                    characteristic.id === editingCharacteristicId ? { ...editedCharacteristic } : characteristic
                )
            );

            setEditingCharacteristicId(null);
            setEditedCharacteristic({});
            alert("Característica de población actualizada correctamente.");
        } catch (error) {
            console.error("Error al actualizar característica de población:", error);
            alert("Error al actualizar característica de población.");
        }
    };

    const handleCancelEdit = () => {
        setEditingAffectedId(null);
        setEditingInterventionId(null);
        setEditingCharacteristicId(null);
        setEditedAffected({});
        setEditedIntervention({});
        setEditedCharacteristic({});
    };

    // ---------- CREACIÓN INLINE ----------
    const handleCreateAffected = () => {
        setCreatingAffected(true);
        // reset newAffected para evitar valores previos
        setNewAffected({
            region: "",
            department: "",
            city: "",
            population_center: "",
            location_entity: "",
        });
    };

    const handleCreateIntervention = () => {
        setCreatingIntervention(true);
        setNewIntervention({
            region: "",
            department: "",
            city: "",
            population_center: "",
            location_entity: "",
        });
    };

    const handleNewAffectedChange = (field, value) => {
        setNewAffected(prev => ({
            ...prev,
            [field]: value,
            ...(field === "region" && { department: "", city: "" }),
            ...(field === "department" && { city: "" }),
        }));
    };

    const handleNewInterventionChange = (field, value) => {
        setNewIntervention(prev => ({
            ...prev,
            [field]: value,
            ...(field === "region" && { department: "", city: "" }),
            ...(field === "department" && { city: "" }),
        }));
    };

    const saveNewAffected = async () => {
        try {
            const payload = { ...newAffected, population_id: populationId };
            const res = await api.post("/affected_population/", payload);
            // el backend debe devolver el objeto creado con id
            setAffectedPopulation(prev => [...prev, res.data]);
            setCreatingAffected(false);
            setNewAffected({
                region: "",
                department: "",
                city: "",
                population_center: "",
                location_entity: "",
            });
            alert("Registro de población afectada creado correctamente.");
        } catch (error) {
            console.error("Error al crear registro afectado:", error);
            alert("Hubo un error al crear el registro.");
        }
    };

    const saveNewIntervention = async () => {
        try {
            const payload = { ...newIntervention, population_id: populationId };
            const res = await api.post("/intervention_population/", payload);
            setInterventionPopulation(prev => [...prev, res.data]);
            setCreatingIntervention(false);
            setNewIntervention({
                region: "",
                department: "",
                city: "",
                population_center: "",
                location_entity: "",
            });
            alert("Registro de población de intervención creado correctamente.");
        } catch (error) {
            console.error("Error al crear registro de intervención:", error);
            alert("Hubo un error al crear el registro.");
        }
    };

    // Auxiliares para dropdowns dependientes
    const getDepartmentOptions = (region) => departments[region] || [];
    const getCityOptions = (department) => cities[department] || [];

    return (
        <div className="container mt-4">
            {/* Affected Population */}
            <div>
                <h2 className="mb-3">Población Afectada</h2>

                <div className="table-responsive">
                    <table className="table table-striped table-bordered">
                        <thead className="table-dark">
                            <tr>
                                <th>ID</th>
                                <th>Región</th>
                                <th>Departamento</th>
                                <th>Ciudad</th>
                                <th>Centro Poblado</th>
                                <th>Resguardo</th>
                                <th>Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            {affectedPopulation.length > 0 ? (
                                affectedPopulation.map((p) => (
                                    <tr key={p.id}>
                                        <td>{p.id}</td>
                                        <td>
                                            {editingAffectedId === p.id ? (
                                                <select
                                                    className="form-control form-control-sm"
                                                    value={editedAffected.region || ''}
                                                    onChange={(e) => handleAffectedChange('region', e.target.value)}
                                                >
                                                    <option value="">Seleccione región</option>
                                                    {regions.map(region => (
                                                        <option key={region} value={region}>{region}</option>
                                                    ))}
                                                </select>
                                            ) : (
                                                p.region
                                            )}
                                        </td>
                                        <td>
                                            {editingAffectedId === p.id ? (
                                                <select
                                                    className="form-control form-control-sm"
                                                    value={editedAffected.department || ''}
                                                    onChange={(e) => handleAffectedChange('department', e.target.value)}
                                                    disabled={!editedAffected.region}
                                                >
                                                    <option value="">Seleccione departamento</option>
                                                    {getDepartmentOptions(editedAffected.region).map(dep => (
                                                        <option key={dep} value={dep}>{dep}</option>
                                                    ))}
                                                </select>
                                            ) : (
                                                p.department
                                            )}
                                        </td>
                                        <td>
                                            {editingAffectedId === p.id ? (
                                                <select
                                                    className="form-control form-control-sm"
                                                    value={editedAffected.city || ''}
                                                    onChange={(e) => handleAffectedChange('city', e.target.value)}
                                                    disabled={!editedAffected.department}
                                                >
                                                    <option value="">Seleccione ciudad</option>
                                                    {getCityOptions(editedAffected.department).map(city => (
                                                        <option key={city} value={city}>{city}</option>
                                                    ))}
                                                </select>
                                            ) : (
                                                p.city
                                            )}
                                        </td>
                                        <td>
                                            {editingAffectedId === p.id ? (
                                                <select
                                                    className="form-control form-control-sm"
                                                    value={editedAffected.population_center || ''}
                                                    onChange={(e) => handleAffectedChange('population_center', e.target.value)}
                                                >
                                                    <option value="">Seleccione centro poblado</option>
                                                    {populationCenters.map(pc => (
                                                        <option key={pc} value={pc}>{pc}</option>
                                                    ))}
                                                </select>
                                            ) : (
                                                p.population_center
                                            )}
                                        </td>
                                        <td>
                                            {editingAffectedId === p.id ? (
                                                <select
                                                    className="form-control form-control-sm"
                                                    value={editedAffected.location_entity || ''}
                                                    onChange={(e) => handleAffectedChange('location_entity', e.target.value)}
                                                >
                                                    <option value="">Seleccione localización</option>
                                                    {locationEntities.map(le => (
                                                        <option key={le} value={le}>{le}</option>
                                                    ))}
                                                </select>
                                            ) : (
                                                p.location_entity
                                            )}
                                        </td>
                                        <td>
                                            {editingAffectedId === p.id ? (
                                                <div>
                                                    <button
                                                        className="btn btn-sm btn-success me-2"
                                                        onClick={handleSaveAffected}
                                                    >
                                                        Guardar
                                                    </button>
                                                    <button
                                                        className="btn btn-sm btn-secondary"
                                                        onClick={handleCancelEdit}
                                                    >
                                                        Cancelar
                                                    </button>
                                                </div>
                                            ) : (
                                                <div>
                                                    <button
                                                        className="btn btn-sm btn-primary me-2"
                                                        onClick={() => handleEditAffected(p)}
                                                    >
                                                        Editar
                                                    </button>
                                                    <button
                                                        className="btn btn-sm btn-danger"
                                                        onClick={() => handleDelete(p.id, "affected")}
                                                    >
                                                        Eliminar
                                                    </button>
                                                </div>
                                            )}
                                        </td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan="7" className="text-center">
                                        No hay registros afectados.
                                    </td>
                                </tr>
                            )}

                            {/* Fila de creación inline */}
                            {creatingAffected && (
                                <tr>
                                    <td>Nuevo</td>
                                    <td>
                                        <select
                                            className="form-control form-control-sm"
                                            value={newAffected.region}
                                            onChange={(e) => handleNewAffectedChange("region", e.target.value)}
                                        >
                                            <option value="">Seleccione región</option>
                                            {regions.map(r => (
                                                <option key={r} value={r}>{r}</option>
                                            ))}
                                        </select>
                                    </td>
                                    <td>
                                        <select
                                            className="form-control form-control-sm"
                                            value={newAffected.department}
                                            onChange={(e) => handleNewAffectedChange("department", e.target.value)}
                                            disabled={!newAffected.region}
                                        >
                                            <option value="">Seleccione departamento</option>
                                            {getDepartmentOptions(newAffected.region).map(dep => (
                                                <option key={dep} value={dep}>{dep}</option>
                                            ))}
                                        </select>
                                    </td>
                                    <td>
                                        <select
                                            className="form-control form-control-sm"
                                            value={newAffected.city}
                                            onChange={(e) => handleNewAffectedChange("city", e.target.value)}
                                            disabled={!newAffected.department}
                                        >
                                            <option value="">Seleccione ciudad</option>
                                            {getCityOptions(newAffected.department).map(c => (
                                                <option key={c} value={c}>{c}</option>
                                            ))}
                                        </select>
                                    </td>
                                    <td>
                                        <select
                                            className="form-control form-control-sm"
                                            value={newAffected.population_center}
                                            onChange={(e) => handleNewAffectedChange("population_center", e.target.value)}
                                        >
                                            <option value="">Seleccione centro poblado</option>
                                            {populationCenters.map(pc => (
                                                <option key={pc} value={pc}>{pc}</option>
                                            ))}
                                        </select>
                                    </td>
                                    <td>
                                        <select
                                            className="form-control form-control-sm"
                                            value={newAffected.location_entity}
                                            onChange={(e) => handleNewAffectedChange("location_entity", e.target.value)}
                                        >
                                            <option value="">Seleccione localización</option>
                                            {locationEntities.map(le => (
                                                <option key={le} value={le}>{le}</option>
                                            ))}
                                        </select>
                                    </td>
                                    <td>
                                        <button className="btn btn-sm btn-success me-2" onClick={saveNewAffected}>
                                            Guardar
                                        </button>
                                        <button
                                            className="btn btn-sm btn-secondary"
                                            onClick={() => setCreatingAffected(false)}
                                        >
                                            Cancelar
                                        </button>
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
                <button
                    className="btn btn-success mb-3"
                    onClick={handleCreateAffected}
                    disabled={creatingAffected}
                >
                    Crear Registro de Afectados
                </button>
            </div>

            {/* Intervention Population */}
            <div className="mt-5">
                <h2 className="mb-3">Población de Intervención</h2>
                <div className="table-responsive">
                    <table className="table table-striped table-bordered">
                        <thead className="table-dark">
                            <tr>
                                <th>ID</th>
                                <th>Región</th>
                                <th>Departamento</th>
                                <th>Ciudad</th>
                                <th>Centro Poblado</th>
                                <th>Resguardo</th>
                                <th>Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            {interventionPopulation.length > 0 ? (
                                interventionPopulation.map((p) => (
                                    <tr key={p.id}>
                                        <td>{p.id}</td>
                                        <td>
                                            {editingInterventionId === p.id ? (
                                                <select
                                                    className="form-control form-control-sm"
                                                    value={editedIntervention.region || ''}
                                                    onChange={(e) => handleInterventionChange('region', e.target.value)}
                                                >
                                                    <option value="">Seleccione región</option>
                                                    {regions.map(region => (
                                                        <option key={region} value={region}>{region}</option>
                                                    ))}
                                                </select>
                                            ) : (
                                                p.region
                                            )}
                                        </td>
                                        <td>
                                            {editingInterventionId === p.id ? (
                                                <select
                                                    className="form-control form-control-sm"
                                                    value={editedIntervention.department || ''}
                                                    onChange={(e) => handleInterventionChange('department', e.target.value)}
                                                    disabled={!editedIntervention.region}
                                                >
                                                    <option value="">Seleccione departamento</option>
                                                    {getDepartmentOptions(editedIntervention.region).map(dep => (
                                                        <option key={dep} value={dep}>{dep}</option>
                                                    ))}
                                                </select>
                                            ) : (
                                                p.department
                                            )}
                                        </td>
                                        <td>
                                            {editingInterventionId === p.id ? (
                                                <select
                                                    className="form-control form-control-sm"
                                                    value={editedIntervention.city || ''}
                                                    onChange={(e) => handleInterventionChange('city', e.target.value)}
                                                    disabled={!editedIntervention.department}
                                                >
                                                    <option value="">Seleccione ciudad</option>
                                                    {getCityOptions(editedIntervention.department).map(city => (
                                                        <option key={city} value={city}>{city}</option>
                                                    ))}
                                                </select>
                                            ) : (
                                                p.city
                                            )}
                                        </td>
                                        <td>
                                            {editingInterventionId === p.id ? (
                                                <select
                                                    className="form-control form-control-sm"
                                                    value={editedIntervention.population_center || ''}
                                                    onChange={(e) => handleInterventionChange('population_center', e.target.value)}
                                                >
                                                    <option value="">Seleccione centro poblado</option>
                                                    {populationCenters.map(pc => (
                                                        <option key={pc} value={pc}>{pc}</option>
                                                    ))}
                                                </select>
                                            ) : (
                                                p.population_center
                                            )}
                                        </td>
                                        <td>
                                            {editingInterventionId === p.id ? (
                                                <select
                                                    className="form-control form-control-sm"
                                                    value={editedIntervention.location_entity || ''}
                                                    onChange={(e) => handleInterventionChange('location_entity', e.target.value)}
                                                >
                                                    <option value="">Seleccione localización</option>
                                                    {locationEntities.map(le => (
                                                        <option key={le} value={le}>{le}</option>
                                                    ))}
                                                </select>
                                            ) : (
                                                p.location_entity
                                            )}
                                        </td>
                                        <td>
                                            {editingInterventionId === p.id ? (
                                                <div>
                                                    <button
                                                        className="btn btn-sm btn-success me-2"
                                                        onClick={handleSaveIntervention}
                                                    >
                                                        Guardar
                                                    </button>
                                                    <button
                                                        className="btn btn-sm btn-secondary"
                                                        onClick={handleCancelEdit}
                                                    >
                                                        Cancelar
                                                    </button>
                                                </div>
                                            ) : (
                                                <div>
                                                    <button
                                                        className="btn btn-sm btn-primary me-2"
                                                        onClick={() => handleEditIntervention(p)}
                                                    >
                                                        Editar
                                                    </button>
                                                    <button
                                                        className="btn btn-sm btn-danger"
                                                        onClick={() => handleDelete(p.id, "intervention")}
                                                    >
                                                        Eliminar
                                                    </button>
                                                </div>
                                            )}
                                        </td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan="7" className="text-center">
                                        No hay registros de intervención.
                                    </td>
                                </tr>
                            )}

                            {/* Fila de creación inline intervención */}
                            {creatingIntervention && (
                                <tr>
                                    <td>Nuevo</td>
                                    <td>
                                        <select
                                            className="form-control form-control-sm"
                                            value={newIntervention.region}
                                            onChange={(e) => handleNewInterventionChange("region", e.target.value)}
                                        >
                                            <option value="">Seleccione región</option>
                                            {regions.map(r => (
                                                <option key={r} value={r}>{r}</option>
                                            ))}
                                        </select>
                                    </td>
                                    <td>
                                        <select
                                            className="form-control form-control-sm"
                                            value={newIntervention.department}
                                            onChange={(e) => handleNewInterventionChange("department", e.target.value)}
                                            disabled={!newIntervention.region}
                                        >
                                            <option value="">Seleccione departamento</option>
                                            {getDepartmentOptions(newIntervention.region).map(dep => (
                                                <option key={dep} value={dep}>{dep}</option>
                                            ))}
                                        </select>
                                    </td>
                                    <td>
                                        <select
                                            className="form-control form-control-sm"
                                            value={newIntervention.city}
                                            onChange={(e) => handleNewInterventionChange("city", e.target.value)}
                                            disabled={!newIntervention.department}
                                        >
                                            <option value="">Seleccione ciudad</option>
                                            {getCityOptions(newIntervention.department).map(c => (
                                                <option key={c} value={c}>{c}</option>
                                            ))}
                                        </select>
                                    </td>
                                    <td>
                                        <select
                                            className="form-control form-control-sm"
                                            value={newIntervention.population_center}
                                            onChange={(e) => handleNewInterventionChange("population_center", e.target.value)}
                                        >
                                            <option value="">Seleccione centro poblado</option>
                                            {populationCenters.map(pc => (
                                                <option key={pc} value={pc}>{pc}</option>
                                            ))}
                                        </select>
                                    </td>
                                    <td>
                                        <select
                                            className="form-control form-control-sm"
                                            value={newIntervention.location_entity}
                                            onChange={(e) => handleNewInterventionChange("location_entity", e.target.value)}
                                        >
                                            <option value="">Seleccione localización</option>
                                            {locationEntities.map(le => (
                                                <option key={le} value={le}>{le}</option>
                                            ))}
                                        </select>
                                    </td>
                                    <td>
                                        <button className="btn btn-sm btn-success me-2" onClick={saveNewIntervention}>
                                            Guardar
                                        </button>
                                        <button
                                            className="btn btn-sm btn-secondary"
                                            onClick={() => setCreatingIntervention(false)}
                                        >
                                            Cancelar
                                        </button>
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
                <button
                    className="btn btn-success mb-3"
                    onClick={handleCreateIntervention}
                    disabled={creatingIntervention}
                >
                    Crear Registro de Intervención
                </button>
            </div>

            {/* Characteristics Population */}
            <div className="mt-5">
                <h2 className="mb-3">Características de la Población</h2>
                <div className="table-responsive">
                    <table className="table table-striped table-bordered">
                        <thead className="table-dark">
                            <tr>
                                <th>Clasificación</th>
                                <th>Detalle</th>
                                <th>Número de personas</th>
                                <th>Fuente de Información</th>
                                <th>Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            {characteristicsPopulation.length > 0 ? (
                                characteristicsPopulation.map((p) => (
                                    <tr key={p.id}>
                                        <td>
                                            {editingCharacteristicId === p.id ? (
                                                <input
                                                    type="text"
                                                    className="form-control form-control-sm"
                                                    value={editedCharacteristic.classification || ''}
                                                    onChange={(e) => handleCharacteristicChange('classification', e.target.value)}
                                                />
                                            ) : (
                                                p.classification
                                            )}
                                        </td>
                                        <td>
                                            {editingCharacteristicId === p.id ? (
                                                <input
                                                    type="text"
                                                    className="form-control form-control-sm"
                                                    value={editedCharacteristic.detail || ''}
                                                    onChange={(e) => handleCharacteristicChange('detail', e.target.value)}
                                                />
                                            ) : (
                                                p.detail
                                            )}
                                        </td>
                                        <td>
                                            {editingCharacteristicId === p.id ? (
                                                <input
                                                    type="number"
                                                    className="form-control form-control-sm"
                                                    value={editedCharacteristic.people_number || 0}
                                                    onChange={(e) => handleCharacteristicChange('people_number', e.target.value)}
                                                />
                                            ) : (
                                                p.people_number
                                            )}
                                        </td>
                                        <td>
                                            {editingCharacteristicId === p.id ? (
                                                <input
                                                    type="text"
                                                    className="form-control form-control-sm"
                                                    value={editedCharacteristic.information || ''}
                                                    onChange={(e) => handleCharacteristicChange('information', e.target.value)}
                                                />
                                            ) : (
                                                p.information
                                            )}
                                        </td>
                                        <td>
                                            {editingCharacteristicId === p.id ? (
                                                <div>
                                                    <button
                                                        className="btn btn-sm btn-success me-2"
                                                        onClick={handleSaveCharacteristic}
                                                    >
                                                        Guardar
                                                    </button>
                                                    <button
                                                        className="btn btn-sm btn-secondary"
                                                        onClick={handleCancelEdit}
                                                    >
                                                        Cancelar
                                                    </button>
                                                </div>
                                            ) : (
                                                <div>
                                                    <button
                                                        className="btn btn-sm btn-primary me-2"
                                                        onClick={() => handleEditCharacteristic(p)}
                                                    >
                                                        Editar
                                                    </button>
                                                    <button
                                                        className="btn btn-sm btn-danger"
                                                        onClick={() => handleDelete(p.id, "characteristic")}
                                                    >
                                                        Eliminar
                                                    </button>
                                                </div>
                                            )}
                                        </td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan="5" className="text-center">
                                        No hay registros de características.
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

export default Population;
