import { useState, useEffect } from "react";
import { FaPlus, FaTrash } from "react-icons/fa";
import "../styles/problemsTree.css";
import api from "../services/api";

function ProblemsTree({ projectId, projectName, ProjectDescription }) {
    const [problem, setProblem] = useState("");
    const [causes, setCauses] = useState([]);
    const [effects, setEffects] = useState([]);
    const [isSaving, setIsSaving] = useState(false);
    const [isProblemEmpty, setIsProblemEmpty] = useState(false);
    const [showErrorPopup, setShowErrorPopup] = useState(false);
    const [currentDescription, setCurrentDescription] = useState("");
    const [magnitudeProblem, setMagnitudeProblem] = useState("");

    // Cargar el árbol de problemas al montar el componente o cuando cambie el projectId
    useEffect(() => {
        const fetchProblemTree = async () => {
            if (!projectId) return;
            try {
                const response = await api.get(`/problems/${projectId}`);
                if (response.data) {
                    const { central_problem, direct_effects = [], direct_causes = [] } = response.data;

                    const mappedEffects = direct_effects.map(effect => ({
                        id: effect.id,
                        text: effect.description,
                        children: (effect.indirect_effects || []).map(indirect => ({
                            id: indirect.id,
                            text: indirect.description,
                        })),
                    }));

                    const mappedCauses = direct_causes.map(cause => ({
                        id: cause.id,
                        text: cause.description,
                        children: (cause.indirect_causes || []).map(indirect => ({
                            id: indirect.id,
                            text: indirect.description,
                        })),
                    }));

                    setProblem(central_problem || "");
                    setCauses(mappedCauses);
                    setEffects(mappedEffects);
                }
            } catch (error) {
                console.error("Error fetching problem tree:", error);
            }
        };
        fetchProblemTree();
    }, [projectId]);

    const addEffect = (type, parentIndex = null) => {
        const newEffect = { text: "", children: [] };
        if (type === "direct") {
            setEffects([...effects, newEffect]);
        } else {
            const updatedEffects = [...effects];
            updatedEffects[parentIndex].children.push(newEffect);
            setEffects(updatedEffects);
        }
    };

    const addCause = (type, parentIndex = null) => {
        const newCause = { text: "", children: [] };
        if (type === "direct") {
            setCauses([...causes, newCause]);
        } else {
            const updatedCauses = [...causes];
            updatedCauses[parentIndex].children.push(newCause);
            setCauses(updatedCauses);
        }
    };

    const removeEffect = async (type, index, parentIndex = null, effectId = null) => {
        if (effectId) {
            try {
                await api.delete(`/effects/${effectId}`);
            } catch (error) {
                console.error("Error eliminando efecto:", error);
            }
        }

        if (type === "direct") {
            setEffects(effects.filter((_, i) => i !== index));
        } else {
            const updatedEffects = [...effects];
            updatedEffects[parentIndex].children = updatedEffects[parentIndex].children.filter((_, i) => i !== index);
            setEffects(updatedEffects);
        }
    };

    const removeCause = async (type, index, parentIndex = null, causeId = null) => {
        if (causeId) {
            try {
                await api.delete(`/causes/${causeId}`);
            } catch (error) {
                console.error("Error eliminando causa:", error);
            }
        }

        if (type === "direct") {
            setCauses(causes.filter((_, i) => i !== index));
        } else {
            const updatedCauses = [...causes];
            updatedCauses[parentIndex].children = updatedCauses[parentIndex].children.filter((_, i) => i !== index);
            setCauses(updatedCauses);
        }
    };

    const generateJson = () => {
        return {
            central_problem: problem,
            current_description: currentDescription,
            magnitude_problem: magnitudeProblem,
            direct_effects: effects.map(effect => ({
                id: effect.id || undefined,  // Usar undefined en lugar de null
                description: effect.text,
                indirect_effects: effect.children.map(child => ({
                    id: child.id || undefined,
                    description: child.text
                }))
            })),
            direct_causes: causes.map(cause => ({
                id: cause.id || undefined,
                description: cause.text,
                indirect_causes: cause.children.map(child => ({
                    id: child.id || undefined,
                    description: child.text
                }))
            }))
        };
    };

    const ErrorPopup = ({ message, onClose }) => {
        return (
            <div className="error-popup-overlay">
                <div className="error-popup">
                    <p>{message}</p>
                    <button onClick={onClose}>Cerrar</button>
                </div>
            </div>
        );
    };

    const sendToFastAPI = async () => {
        // Validar campo problema general
        if (!problem.trim()) {
            setIsProblemEmpty(true);
            setShowErrorPopup(true);
            return;
        }

        setIsSaving(true);
        const jsonData = generateJson();

        try {
            const response = await api.post("/problems", jsonData);

            if (!response.data) throw new Error("Error al crear el problema");

            const { id: problemId } = response.data;
            if (problemId && projectId) {
                const updateData = {
                    name: projectName,
                    description: ProjectDescription,
                    problem_id: problemId
                };
                await api.put(`/projects/${projectId}`, updateData);
            }
        } catch (error) {
            console.error("Error:", error);
        } finally {
            setIsSaving(false);
        }
    };

    const updateProblemTree = async () => {
        if (!projectId) return;

        setIsSaving(true);
        const jsonData = generateJson();
        console.log("Datos enviados para actualización:", jsonData); // Para depuración

        try {
            const response = await api.put(`/problems/${projectId}`, jsonData);
            console.log("Árbol de problemas actualizado correctamente", response.data);

            // Opcional: Actualizar el estado local con la respuesta del servidor
            if (response.data) {
                const { central_problem, direct_effects = [], direct_causes = [] } = response.data;

                const mappedEffects = direct_effects.map(effect => ({
                    id: effect.id,
                    text: effect.description,
                    children: (effect.indirect_effects || []).map(indirect => ({
                        id: indirect.id,
                        text: indirect.description,
                    })),
                }));

                const mappedCauses = direct_causes.map(cause => ({
                    id: cause.id,
                    text: cause.description,
                    children: (cause.indirect_causes || []).map(indirect => ({
                        id: indirect.id,
                        text: indirect.description,
                    })),
                }));

                setProblem(central_problem || "");
                setCauses(mappedCauses);
                setEffects(mappedEffects);
            }
        } catch (error) {
            console.error("Error actualizando árbol de problemas:", error.response?.data || error.message);
        } finally {
            setIsSaving(false);
        }
    };



    return (
        <div className="problems-tree-container">
            <h3>Árbol de Problemas</h3>

            <div className="tree">
                <div className="branches">
                    {effects.map((effect, index) => (
                        <div key={index} className="effect">

                            <div className="effect-input-container">
                                <input
                                    type="text"
                                    placeholder="Efecto directo"
                                    value={effect.text}
                                    onChange={(e) => {
                                        const updated = [...effects];
                                        updated[index].text = e.target.value;
                                        setEffects(updated);
                                    }}
                                />
                                <button
                                    className="icon-button delete-button"
                                    onClick={() => removeEffect("direct", index)}
                                >
                                    <FaTrash />
                                </button>
                            </div>
                            <div className="sub-effects">
                                {effect.children?.map((child, childIndex) => (
                                    <div key={childIndex} className="effect-input-container">
                                        <input
                                            type="text"
                                            placeholder="Efecto Indirecto"
                                            value={child.text}
                                            onChange={(e) => {
                                                const updated = [...effects];
                                                updated[index].children[childIndex].text = e.target.value;
                                                setEffects(updated);
                                            }}
                                        />
                                        <button
                                            className="icon-button delete-button"
                                            onClick={() => removeEffect("indirect", childIndex, index)}
                                        >
                                            <FaTrash />
                                        </button>
                                    </div>
                                ))}
                            </div>
                            <button
                                className="icon-button add-button"
                                onClick={() => addEffect("indirect", index)}
                            >
                                <FaPlus /> Agregar Efecto Indirecto
                            </button>
                        </div>
                    ))}
                    <button
                        className="icon-button add-button"
                        onClick={() => addEffect("direct")}
                    >
                        <FaPlus /> Agregar Efecto Directo
                    </button>
                </div>

                <div className="trunk">
                    <input
                        type="text"
                        placeholder="Problema general"
                        value={problem}
                        onChange={(e) => {
                            setProblem(e.target.value);
                            // Resetear el estado de error cuando el usuario empiece a escribir
                            if (isProblemEmpty && e.target.value.trim()) {
                                setIsProblemEmpty(false);
                            }
                        }}
                        className={isProblemEmpty ? "error-input" : ""}
                    />
                </div>

                <div className="roots">
                    {causes.map((cause, index) => (
                        <div key={index} className="cause">
                            <div className="cause-input-container">
                                <input
                                    type="text"
                                    placeholder="Causa directa"
                                    value={cause.text}
                                    onChange={(e) => {
                                        const updated = [...causes];
                                        updated[index].text = e.target.value;
                                        setCauses(updated);
                                    }}
                                />
                                <button
                                    className="icon-button delete-button"
                                    onClick={() => removeCause("direct", index)}
                                >
                                    <FaTrash />
                                </button>
                            </div>
                            <div className="sub-causes">
                                {cause.children?.map((child, childIndex) => (
                                    <div key={childIndex} className="cause-input-container">
                                        <input
                                            type="text"
                                            placeholder="Causa indirecta"
                                            value={child.text}
                                            onChange={(e) => {
                                                const updated = [...causes];
                                                updated[index].children[childIndex].text = e.target.value;
                                                setCauses(updated);
                                            }}
                                        />
                                        <button
                                            className="icon-button delete-button"
                                            onClick={() => removeCause("indirect", childIndex, index)}
                                        >
                                            <FaTrash />
                                        </button>
                                    </div>
                                ))}
                            </div>
                            <button
                                className="icon-button add-button"
                                onClick={() => addCause("indirect", index)}
                            >
                                <FaPlus /> Agregar Causa Indirecta
                            </button>
                        </div>
                    ))}
                    <button
                        className="icon-button add-button"
                        onClick={() => addCause("direct")}
                    >
                        <FaPlus /> Agregar Causa Directa
                    </button>
                </div>
            </div>
            {showErrorPopup && (
                <ErrorPopup
                    message="El campo Problema general es obligatorio. Por favor, complételo antes de guardar."
                    onClose={() => setShowErrorPopup(false)}
                />
            )}
            <div className="trunk">
                <input
                    type="text"
                    placeholder="Descripción de la situación existente con respecto al problema"
                    value={currentDescription}
                    onChange={(e) => setCurrentDescription(e.target.value)}
                    className={isProblemEmpty ? "error-input" : ""}
                />
            </div>
            <div className="trunk">
                <input
                    type="text"
                    placeholder="Magnitud actual del problema e indicadores de referencia"
                    value={magnitudeProblem}
                    onChange={(e) => setMagnitudeProblem(e.target.value)}
                    className={isProblemEmpty ? "error-input" : ""}
                />
                <div className="buttons-container">
                    <div className="action-buttons">
                        {/* <button
                        className="action-button submit-button"
                        onClick={sendToFastAPI}
                        disabled={isSaving}
                    >
                        {isSaving ? "Guardando..." : "Guardar"}
                    </button> */}
                        <button
                            className="action-button update-button"
                            onClick={updateProblemTree}
                            disabled={isSaving}
                        >
                            {isSaving ? "Actualizando..." : "Actualizar"}
                        </button>
                    </div>

                </div>
            </div>
        </div>


    );
}

export default ProblemsTree;