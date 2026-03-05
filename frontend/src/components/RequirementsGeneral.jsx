import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

function RequirementsGeneral({ projectId }) {
    const navigate = useNavigate();
    const [requirementsGeneralId, setRequirementsGeneralId] = useState(null);
    const [requirementsAnalysis, setRequirementsAnalysis] = useState("");
    const [requirements, setRequirements] = useState([]);


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

    const fetchRequirements = async () => {

        try {

            const res = await api.get(`/requirements_general/${projectId}`);

            const data = res.data;


            if (data && data.length > 0) {

                const req = data[0];


                setRequirementsGeneralId(req.id);

                setRequirementsAnalysis(req.requirements_analysis || "");

                setRequirements(req.requirements || []);

            }


        } catch (error) {

            console.error("Error cargando requirements:", error);

        }

    };



    useEffect(() => {

        if (projectId)

            fetchRequirements();

    }, [projectId]);



    // ---------- GUARDAR GENERAL ----------

    const handleSubmit = async () => {


        const payload = {

            project_id: projectId,

            requirements_analysis: requirementsAnalysis,

            requirements: requirements

        };


        try {

            if (requirementsGeneralId) {

                await api.put(

                    `/requirements_general/${requirementsGeneralId}`,

                    payload

                );

            }

            else {

                const res = await api.post(

                    `/requirements_general`,

                    payload

                );

                setRequirementsGeneralId(res.data.id);

            }


            alert("Necesidades guardadas");

            fetchRequirements();


        } catch (err) {

            console.error(err);

            alert("Error guardando");

        }

    };



    // ---------- DELETE ----------

    const handleDelete = async (id) => {

        if (!window.confirm("Eliminar registro?"))

            return;


        await api.delete(`/requirements/${id}`);


        setRequirements(prev =>

            prev.filter(r => r.id !== id)

        );

    };



    // ---------- EDIT ----------

    const handleEdit = (r) => {

        setEditingRequirementId(r.id);

        setEditedRequirement({ ...r });

    };



    const handleSave = async () => {

        await api.put(

            `/requirements/${editingRequirementId}`,

            editedRequirement

        );


        setRequirements(prev =>

            prev.map(r =>

                r.id === editingRequirementId

                    ? editedRequirement

                    : r

            )

        );


        setEditingRequirementId(null);

    };



    const cancelEdit = () => {

        setEditingRequirementId(null);

        setEditedRequirement({});

    };



    // ---------- CREAR ----------

    const saveNewRequirement = async () => {

        const payload = {

            ...newRequirement,

            requirements_general_id: requirementsGeneralId

        };


        const res = await api.post(

            "/requirements/",

            payload

        );


        setRequirements(prev =>

            [...prev, res.data]

        );


        setCreatingRequirement(false);


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

    };



    return (

        <div className="container mt-4">


            {/* ---------- ANALYSIS ---------- */}

            <h2>Análisis de Necesidades</h2>

            <textarea

                className="form-control mb-4"

                value={requirementsAnalysis}

                onChange={e =>

                    setRequirementsAnalysis(e.target.value)

                }

            />


            {/* ---------- TABLA ---------- */}

            <h2>Necesidades</h2>


            <table className="table table-bordered">


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

                                {editingRequirementId === r.id ?

                                    <input

                                        className="form-control form-control-sm"

                                        value={editedRequirement.good_service_name || ""}

                                        onChange={e =>

                                            setEditedRequirement({

                                                ...editedRequirement,

                                                good_service_name: e.target.value

                                            })

                                        }

                                    />

                                    :

                                    r.good_service_name}

                            </td>



                            <td>

                                {editingRequirementId === r.id ?

                                    <textarea

                                        className="form-control form-control-sm"

                                        value={editedRequirement.good_service_description || ""}

                                        onChange={e =>

                                            setEditedRequirement({

                                                ...editedRequirement,

                                                good_service_description: e.target.value

                                            })

                                        }

                                    />

                                    :

                                    r.good_service_description}

                            </td>



                            <td>

                                {editingRequirementId === r.id ?

                                    <textarea

                                        className="form-control form-control-sm"

                                        value={editedRequirement.supply_description || ""}

                                        onChange={e =>

                                            setEditedRequirement({

                                                ...editedRequirement,

                                                supply_description: e.target.value

                                            })

                                        }

                                    />

                                    :

                                    r.supply_description}

                            </td>



                            <td>

                                {editingRequirementId === r.id ?

                                    <textarea

                                        className="form-control form-control-sm"

                                        value={editedRequirement.demand_description || ""}

                                        onChange={e =>

                                            setEditedRequirement({

                                                ...editedRequirement,

                                                demand_description: e.target.value

                                            })

                                        }

                                    />

                                    :

                                    r.demand_description}

                            </td>



                            <td>

                                {editingRequirementId === r.id ?

                                    <input

                                        className="form-control form-control-sm"

                                        value={editedRequirement.unit_of_measure || ""}

                                        onChange={e =>

                                            setEditedRequirement({

                                                ...editedRequirement,

                                                unit_of_measure: e.target.value

                                            })

                                        }

                                    />

                                    :

                                    r.unit_of_measure}

                            </td>



                            <td>

                                {editingRequirementId === r.id ?

                                    <input

                                        type="number"

                                        className="form-control form-control-sm"

                                        value={editedRequirement.start_year || ""}

                                        onChange={e =>

                                            setEditedRequirement({

                                                ...editedRequirement,

                                                start_year: e.target.value

                                            })

                                        }

                                    />

                                    :

                                    r.start_year}

                            </td>



                            <td>

                                {editingRequirementId === r.id ?

                                    <input

                                        type="number"

                                        className="form-control form-control-sm"

                                        value={editedRequirement.end_year || ""}

                                        onChange={e =>

                                            setEditedRequirement({

                                                ...editedRequirement,

                                                end_year: e.target.value

                                            })

                                        }

                                    />

                                    :

                                    r.end_year}

                            </td>



                            <td>

                                {editingRequirementId === r.id ?

                                    <input

                                        type="number"

                                        className="form-control form-control-sm"

                                        value={editedRequirement.last_projected_year || ""}

                                        onChange={e =>

                                            setEditedRequirement({

                                                ...editedRequirement,

                                                last_projected_year: e.target.value

                                            })

                                        }

                                    />

                                    :

                                    r.last_projected_year}

                            </td>



                            <td>

                                {editingRequirementId === r.id ?

                                    <>

                                        <button

                                            className="btn btn-sm btn-success me-2"

                                            onClick={handleSave}

                                        >

                                            Guardar

                                        </button>


                                        <button

                                            className="btn btn-sm btn-secondary"

                                            onClick={cancelEdit}

                                        >

                                            Cancelar

                                        </button>

                                    </>

                                    :

                                    <>

                                        <button

                                            className="btn btn-sm btn-primary me-2"

                                            onClick={() => handleEdit(r)}

                                        >

                                            Editar

                                        </button>


                                        <button

                                            className="btn btn-sm btn-danger"

                                            onClick={() => handleDelete(r.id)}

                                        >

                                            Eliminar

                                        </button>

                                    </>

                                }

                            </td>


                        </tr>

                    ))}



                    {/* NUEVO */}


                    {creatingRequirement && (

                        <tr>


                            <td>Nuevo</td>


                            <td>

                                <input

                                    className="form-control form-control-sm"

                                    value={newRequirement.good_service_name}

                                    onChange={e =>

                                        setNewRequirement({

                                            ...newRequirement,

                                            good_service_name: e.target.value

                                        })

                                    }

                                />

                            </td>


                            <td>

                                <textarea

                                    className="form-control form-control-sm"

                                    value={newRequirement.good_service_description}

                                    onChange={e =>

                                        setNewRequirement({

                                            ...newRequirement,

                                            good_service_description: e.target.value

                                        })

                                    }

                                />

                            </td>


                            <td>

                                <textarea

                                    className="form-control form-control-sm"

                                    value={newRequirement.supply_description}

                                    onChange={e =>

                                        setNewRequirement({

                                            ...newRequirement,

                                            supply_description: e.target.value

                                        })

                                    }

                                />

                            </td>


                            <td>

                                <textarea

                                    className="form-control form-control-sm"

                                    value={newRequirement.demand_description}

                                    onChange={e =>

                                        setNewRequirement({

                                            ...newRequirement,

                                            demand_description: e.target.value

                                        })

                                    }

                                />

                            </td>


                            <td>

                                <input

                                    className="form-control form-control-sm"

                                    value={newRequirement.unit_of_measure}

                                    onChange={e =>

                                        setNewRequirement({

                                            ...newRequirement,

                                            unit_of_measure: e.target.value

                                        })

                                    }

                                />

                            </td>


                            <td>

                                <input

                                    type="number"

                                    className="form-control form-control-sm"

                                    value={newRequirement.start_year}

                                    onChange={e =>

                                        setNewRequirement({

                                            ...newRequirement,

                                            start_year: e.target.value

                                        })

                                    }

                                />

                            </td>


                            <td>

                                <input

                                    type="number"

                                    className="form-control form-control-sm"

                                    value={newRequirement.end_year}

                                    onChange={e =>

                                        setNewRequirement({

                                            ...newRequirement,

                                            end_year: e.target.value

                                        })

                                    }

                                />

                            </td>


                            <td>

                                <input

                                    type="number"

                                    className="form-control form-control-sm"

                                    value={newRequirement.last_projected_year}

                                    onChange={e =>

                                        setNewRequirement({

                                            ...newRequirement,

                                            last_projected_year: e.target.value

                                        })

                                    }

                                />

                            </td>


                            <td>

                                <button

                                    className="btn btn-sm btn-success me-2"

                                    onClick={saveNewRequirement}

                                >

                                    Guardar

                                </button>


                                <button

                                    className="btn btn-sm btn-secondary"

                                    onClick={() =>

                                        setCreatingRequirement(false)

                                    }

                                >

                                    Cancelar

                                </button>

                            </td>


                        </tr>

                    )}


                </tbody>

            </table>



            <button

                className="btn btn-success mb-4"

                onClick={() => setCreatingRequirement(true)}

                disabled={creatingRequirement}

            >

                Crear Necesidad

            </button>



            <div>

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

export default RequirementsGeneral;