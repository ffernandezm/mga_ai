import { useState, useEffect } from "react";
import { FaPlus, FaTrash, FaExclamationTriangle } from "react-icons/fa";
import "../styles/problemsTree.css";
import api from "../services/api";
import ConfirmationPopup from "./ConfirmationPopup";
import SuccessMessage from "./SuccessMessage";

function ProblemsTree({ projectId, projectName, ProjectDescription }) {
    const [problem, setProblem] = useState("");
    const [causes, setCauses] = useState([]);
    const [effects, setEffects] = useState([]);
    const [isSaving, setIsSaving] = useState(false);
    const [isProblemEmpty, setIsProblemEmpty] = useState(false);
    const [showErrorPopup, setShowErrorPopup] = useState(false);
    const [currentDescription, setCurrentDescription] = useState("");
    const [magnitudeProblem, setMagnitudeProblem] = useState("");
    const [refreshTrigger, setRefreshTrigger] = useState(0);

    // Estados para los nuevos componentes
    const [showConfirmation, setShowConfirmation] = useState(false);
    const [confirmationConfig, setConfirmationConfig] = useState({});
    const [showSuccess, setShowSuccess] = useState(false);
    const [successMessage, setSuccessMessage] = useState("");

    // Cargar el árbol de problemas
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
    }, [projectId, refreshTrigger]);

    // Validaciones
    const validateMinimumRequirements = () => {
        const hasDirectEffect = effects.length > 0;
        const hasDirectCause = causes.length > 0;
        const hasIndirectEffect = effects.some(effect => effect.children && effect.children.length > 0);
        const hasIndirectCause = causes.some(cause => cause.children && cause.children.length > 0);

        return {
            isValid: hasDirectEffect && hasDirectCause && hasIndirectEffect && hasIndirectCause,
            messages: [
                !hasDirectEffect && "Al menos un Efecto Directo",
                !hasDirectCause && "Al menos una Causa Directa",
                !hasIndirectEffect && "Al menos un Efecto Indirecto",
                !hasIndirectCause && "Al menos una Causa Indirecta"
            ].filter(Boolean)
        };
    };

    const showSuccessMessage = (message) => {
        setSuccessMessage(message);
        setShowSuccess(true);
    };

    const addEffect = (type, parentIndex = null) => {
        const newEffect = {
            text: "",
            children: []
        };

        if (type === "direct") {
            setEffects([...effects, newEffect]);
        } else {
            const updatedEffects = [...effects];
            updatedEffects[parentIndex].children.push(newEffect);
            setEffects(updatedEffects);
        }
    };

    const addCause = (type, parentIndex = null) => {
        const newCause = {
            text: "",
            children: []
        };

        if (type === "direct") {
            setCauses([...causes, newCause]);
        } else {
            const updatedCauses = [...causes];
            updatedCauses[parentIndex].children.push(newCause);
            setCauses(updatedCauses);
        }
    };

    // Función para mostrar confirmación de eliminación
    const confirmDelete = (config) => {
        setConfirmationConfig(config);
        setShowConfirmation(true);
    };

    const removeEffect = async (type, index, parentIndex = null, effectId = null, effectText = "") => {
        if (type === "direct" && effectId) {
            try {
                await api.delete(`/direct_effects/${projectId}/${effectId}`);
                showSuccessMessage("Efecto directo y sus efectos indirectos eliminados correctamente");
            } catch (error) {
                console.error("Error eliminando efecto directo:", error);
                return;
            }
        } else if (type === "indirect" && effectId) {
            try {
                const directEffect = effects[parentIndex];
                await api.delete(`/indirect_effects/${directEffect.id}/${effectId}`);
                showSuccessMessage("Efecto indirecto eliminado correctamente");
            } catch (error) {
                console.error("Error eliminando efecto indirecto:", error);
                return;
            }
        }

        if (type === "direct") {
            setEffects(effects.filter((_, i) => i !== index));
        } else {
            const updatedEffects = [...effects];
            updatedEffects[parentIndex].children = updatedEffects[parentIndex].children.filter((_, i) => i !== index);
            setEffects(updatedEffects);
        }

        setRefreshTrigger(prev => prev + 1);
    };

    const removeCause = async (type, index, parentIndex = null, causeId = null, causeText = "") => {
        if (type === "direct" && causeId) {
            try {
                await api.delete(`/direct_causes/${projectId}/${causeId}`);
                showSuccessMessage("Causa directa y sus causas indirectas eliminadas correctamente");
            } catch (error) {
                console.error("Error eliminando causa directa:", error);
                return;
            }
        } else if (type === "indirect" && causeId) {
            try {
                const directCause = causes[parentIndex];
                await api.delete(`/indirect_causes/${directCause.id}/${causeId}`);
                showSuccessMessage("Causa indirecta eliminada correctamente");
            } catch (error) {
                console.error("Error eliminando causa indirecta:", error);
                return;
            }
        }

        if (type === "direct") {
            setCauses(causes.filter((_, i) => i !== index));
        } else {
            const updatedCauses = [...causes];
            updatedCauses[parentIndex].children = updatedCauses[parentIndex].children.filter((_, i) => i !== index);
            setCauses(updatedCauses);
        }

        setRefreshTrigger(prev => prev + 1);
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
                    <div className="error-icon">
                        <FaExclamationTriangle />
                    </div>
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

        // Validar requisitos mínimos
        const validation = validateMinimumRequirements();
        if (!validation.isValid) {
            setShowErrorPopup(true);
            return;
        }

        setIsSaving(true);
        const jsonData = generateJson();

        try {
            const response = await api.put(`/problems/${projectId}`, jsonData);
            console.log("Árbol de problemas actualizado correctamente", response.data);
            setRefreshTrigger(prev => prev + 1);
            showSuccessMessage("Árbol de problemas actualizado correctamente");
        } catch (error) {
            console.error("Error actualizando árbol de problemas:", error.response?.data || error.message);
            setShowErrorPopup(true);
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
                                    onClick={() => confirmDelete({
                                        type: "effect",
                                        action: () => removeEffect("direct", index, null, effect.id, effect.text),
                                        title: "Eliminar Efecto Directo",
                                        message: `¿Está seguro de que desea eliminar el efecto directo "${effect.text || 'sin nombre'}"? Esta acción también eliminará todos sus efectos indirectos.`
                                    })}
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
                                            onClick={() => confirmDelete({
                                                type: "effect",
                                                action: () => removeEffect("indirect", childIndex, index, child.id, child.text),
                                                title: "Eliminar Efecto Indirecto",
                                                message: `¿Está seguro de que desea eliminar el efecto indirecto "${child.text || 'sin nombre'}"?`
                                            })}
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
                    <div className="problem-general-container">
                        <label className="problem-general-label">Problema General *</label>
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
                                    onClick={() => confirmDelete({
                                        type: "cause",
                                        action: () => removeCause("direct", index, null, cause.id, cause.text),
                                        title: "Eliminar Causa Directa",
                                        message: `¿Está seguro de que desea eliminar la causa directa "${cause.text || 'sin nombre'}"? Esta acción también eliminará todas sus causas indirectas.`
                                    })}
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
                                            onClick={() => confirmDelete({
                                                type: "cause",
                                                action: () => removeCause("indirect", childIndex, index, child.id, child.text),
                                                title: "Eliminar Causa Indirecta",
                                                message: `¿Está seguro de que desea eliminar la causa indirecta "${child.text || 'sin nombre'}"?`
                                            })}
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
                    message={
                        !problem.trim()
                            ? "El campo Problema general es obligatorio. Por favor, complételo antes de guardar."
                            : "Debe cumplir con los requisitos mínimos: Al menos un Efecto Directo, un Efecto Indirecto, una Causa Directa y una Causa Indirecta."
                    }
                    onClose={() => setShowErrorPopup(false)}
                />
            )}

            <div className="additional-fields">
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
                </div>
            </div>

            {/* Componentes de Confirmación y Éxito */}
            <ConfirmationPopup
                isOpen={showConfirmation}
                onConfirm={() => {
                    confirmationConfig.action();
                    setShowConfirmation(false);
                }}
                onCancel={() => setShowConfirmation(false)}
                title={confirmationConfig.title}
                message={confirmationConfig.message}
            />

            <SuccessMessage
                message={successMessage}
                isVisible={showSuccess}
                onHide={() => setShowSuccess(false)}
            />
        </div>
    );
}

export default ProblemsTree;