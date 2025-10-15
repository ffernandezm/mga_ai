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
    const [refreshTrigger, setRefreshTrigger] = useState(0); // 👈 Nuevo estado para forzar re-render

    // Cargar el árbol de problemas - ahora se ejecuta cuando cambia projectId O refreshTrigger
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

                    // También cargar los otros campos si existen en la respuesta
                    if (response.data.current_description) {
                        setCurrentDescription(response.data.current_description);
                    }
                    if (response.data.magnitude_problem) {
                        setMagnitudeProblem(response.data.magnitude_problem);
                    }
                }
            } catch (error) {
                console.error("Error fetching problem tree:", error);
            }
        };
        fetchProblemTree();
    }, [projectId, refreshTrigger]); // 👈 Ahora también depende de refreshTrigger

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
                // Forzar recarga después de eliminar
                setRefreshTrigger(prev => prev + 1);
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
                // Forzar recarga después de eliminar
                setRefreshTrigger(prev => prev + 1);
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
                id: effect.id || undefined,
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

    const updateProblemTree = async () => {
        if (!projectId) return;

        // Validar campo problema general
        if (!problem.trim()) {
            setIsProblemEmpty(true);
            setShowErrorPopup(true);
            return;
        }

        setIsSaving(true);
        const jsonData = generateJson();
        console.log("Datos enviados para actualización:", jsonData);

        try {
            const response = await api.put(`/problems/${projectId}`, jsonData);
            console.log("Árbol de problemas actualizado correctamente", response.data);

            // 👈 FORZAR RE-RENDER DESPUÉS DE ACTUALIZAR
            setRefreshTrigger(prev => prev + 1);

            // También puedes mostrar un mensaje de éxito
            alert("Árbol de problemas actualizado correctamente");

        } catch (error) {
            console.error("Error actualizando árbol de problemas:", error.response?.data || error.message);
            alert("Error al actualizar el árbol de problemas");
        } finally {
            setIsSaving(false);
        }
    };

    // Función para limpiar todos los campos (opcional)
    const clearAll = () => {
        setProblem("");
        setCauses([]);
        setEffects([]);
        setCurrentDescription("");
        setMagnitudeProblem("");
    };

    return (
        <div className="problems-tree-container">
            <h3>Árbol de Problemas</h3>

            {/* Botón para recargar manualmente (útil para debugging) */}
            {/* <div style={{ marginBottom: '10px' }}>
                <button 
                    onClick={() => setRefreshTrigger(prev => prev + 1)}
                    className="btn btn-sm btn-outline-secondary"
                >
                    🔄 Recargar Datos
                </button>
            </div> */}

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
                                    onClick={() => removeEffect("direct", index, null, effect.id)}
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
                                            onClick={() => removeEffect("indirect", childIndex, index, child.id)}
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
                                    onClick={() => removeCause("direct", index, null, cause.id)}
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
                                            onClick={() => removeCause("indirect", childIndex, index, child.id)}
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
                />
            </div>

            <div className="trunk">
                <input
                    type="text"
                    placeholder="Magnitud actual del problema e indicadores de referencia"
                    value={magnitudeProblem}
                    onChange={(e) => setMagnitudeProblem(e.target.value)}
                />
            </div>

            <div className="buttons-container">
                <div className="action-buttons">
                    <button
                        className="action-button update-button"
                        onClick={updateProblemTree}
                        disabled={isSaving}
                    >
                        {isSaving ? "Actualizando..." : "Guardar/Actualizar"}
                    </button>

                    {/* Botón opcional para limpiar */}
                    {/* <button
                        className="action-button clear-button"
                        onClick={clearAll}
                        style={{marginLeft: '10px', backgroundColor: '#dc3545'}}
                    >
                        Limpiar Todo
                    </button> */}
                </div>
            </div>
        </div>
    );
}

export default ProblemsTree;