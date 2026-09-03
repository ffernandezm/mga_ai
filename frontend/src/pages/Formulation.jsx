import { useState, useEffect } from "react";
import { useParams, useNavigate, useLocation } from "react-router-dom";
import { ChevronLeft, ChevronRight, ClipboardCheck } from "lucide-react";
import DevelopmentPlan from "../components/DevelopmentPlan";
import ProblemsTree from "../components/ProblemsTree";
import Participants from "../components/Participants";
import Population from "../components/Population";
import Objectives from "../components/Objectives";
import AlternativesGeneral from "../components/AlternativesGeneral";
import RequirementsGeneral from "../components/RequirementsGeneral";
import TechnicalAnalysis from "../components/TechnicalAnalysis";
import LocalizationGeneral from "../components/LocalizationGeneral";
import ValueChain from "../components/ValueChain";


import Chatbot from "../components/Chatbot";
import ProjectHeader from "../components/ProjectHeader";
import SectionValidationModal from "../components/SectionValidationModal";
import api from "../services/api";
import { MGASection, MGA_SECTION_METADATA, MGA_VALIDATION_SECTION_TO_TAB } from "../utils/constants";
import "./Formulation.css";

function Formulation() {
    const { id } = useParams();
    const navigate = useNavigate();
    const location = useLocation(); // 👈 Para leer query params

    const [activeTab, setActiveTab] = useState("development_plans");
    const [project, setProject] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [sectionStates, setSectionStates] = useState({});
    const [validationModal, setValidationModal] = useState(null);
    const [review, setReview] = useState(null);
    const [participantId, setParticipantId] = useState("");
    const [evaluationSession, setEvaluationSession] = useState(null);
    const [suggestionApplication, setSuggestionApplication] = useState(null);

    const applySuggestedChanges = (changes) => {
        setSuggestionApplication({ id: Date.now(), changes });
    };

    const sectionOrder = Object.values(MGASection);

    const [chatOpen, setChatOpen] = useState(() => {
        const savedState = localStorage.getItem("mga_chat_open");

        return savedState !== null
            ? JSON.parse(savedState)
            : true;
    });

    useEffect(() => {
        const params = new URLSearchParams(location.search);
        const tab = params.get("tab");
        if (!tab || !sectionOrder.includes(tab)) return;

        const validateDirectAccess = async () => {
            try {
                const { sections, states } = await loadValidation();
                const targetIndex = sectionOrder.indexOf(tab);
                const blocker = sections.find(
                    (item) => sectionOrder.indexOf(MGA_VALIDATION_SECTION_TO_TAB[item.section]) < targetIndex && !item.complete
                );
                if (blocker) {
                    const blockerTab = MGA_VALIDATION_SECTION_TO_TAB[blocker.section];
                    setActiveTab(blockerTab);
                    setValidationModal({ ...blocker, tab: blockerTab });
                    navigate(`/projects/${id}/formulation?tab=${blockerTab}`, { replace: true });
                } else {
                    setActiveTab(tab);
                }
            } catch (validationError) {
                console.error("No se pudo validar el acceso a la sección", validationError);
            }
        };
        validateDirectAccess();
    }, [id, location.search]);

    useEffect(() => {
        const fetchProject = async () => {
            try {
                const response = await api.get(`/projects/${id}`);
                setProject(response.data);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };
        fetchProject();
    }, [id]);

    useEffect(() => {
        const restoreEvaluationSession = async () => {
            const storedId = localStorage.getItem("mga_evaluation_session_id");
            if (!storedId) return;
            try {
                const session = await api.get(`/evaluation/sessions/${storedId}`);
                if (session.project_id === Number(id) && !session.ended_at) {
                    setEvaluationSession(session);
                    setParticipantId(session.participant_id);
                } else {
                    localStorage.removeItem("mga_evaluation_session_id");
                }
            } catch {
                localStorage.removeItem("mga_evaluation_session_id");
            }
        };
        void restoreEvaluationSession();
    }, [id]);

    useEffect(() => {
        localStorage.setItem(
            "mga_chat_open",
            JSON.stringify(chatOpen)
        );
    }, [chatOpen]);

    const recordEvaluationEvent = async (eventType, section, payload = {}) => {
        if (!evaluationSession?.id) return;
        try {
            await api.post(`/evaluation/sessions/${evaluationSession.id}/events`, {
                event_type: eventType,
                section,
                payload,
            });
        } catch (telemetryError) {
            console.warn("No se pudo registrar telemetría de evaluación", telemetryError);
        }
    };

    const loadValidation = async () => {
        const response = await api.get(`/projects/${id}/sections/validation`);
        const states = Object.fromEntries(response.data.map((item) => [MGA_VALIDATION_SECTION_TO_TAB[item.section], item]));
        setSectionStates(states);
        await Promise.all(response.data.map((item) => recordEvaluationEvent("validation_run", MGA_VALIDATION_SECTION_TO_TAB[item.section], {
            errors_count: item.missing_fields.length + item.blocking_rules.length,
            warnings_count: item.warnings.length,
            completed: item.complete,
        })));
        return { sections: response.data, states };
    };

    useEffect(() => {
        if (evaluationSession?.id) void recordEvaluationEvent("section_started", activeTab);
    }, [activeTab, evaluationSession?.id]);

    const toggleChat = () => {
        setChatOpen(previousState => !previousState);
    };

    const handleTabChange = async (tab) => {
        const currentIndex = sectionOrder.indexOf(activeTab);
        const targetIndex = sectionOrder.indexOf(tab);
        if (targetIndex > currentIndex) {
            try {
                const { sections, states } = await loadValidation();
                if (states[activeTab]?.complete) await recordEvaluationEvent("section_finished", activeTab);
                const blocker = sections.find(
                    (item) => sectionOrder.indexOf(MGA_VALIDATION_SECTION_TO_TAB[item.section]) < targetIndex && !item.complete
                );
                if (blocker) {
                    const blockerTab = MGA_VALIDATION_SECTION_TO_TAB[blocker.section];
                    setValidationModal({ ...blocker, tab: blockerTab });
                    setActiveTab(blockerTab);
                    navigate(`/projects/${id}/formulation?tab=${blockerTab}`, { replace: true });
                    return;
                }
            } catch (validationError) {
                console.error("No se pudo validar la navegación", validationError);
                return;
            }
        }
        setActiveTab(tab);
        navigate(`/projects/${id}/formulation?tab=${tab}`, { replace: true });
    };

    const handleReview = async () => {
        try {
            const response = await api.get(`/projects/${id}/formulation/review`);
            setReview(response.data);
        } catch (reviewError) {
            console.error("No se pudo revisar la formulación", reviewError);
        }
    };

    const startEvaluation = async () => {
        if (!participantId.trim()) return;
        try {
            const response = await api.post("/evaluation/sessions", {
                participant_id: participantId.trim(), project_id: Number(id), task: "formulación MGA",
            });
            setEvaluationSession(response.data);
            localStorage.setItem("mga_evaluation_session_id", String(response.data.id));
        } catch (evaluationError) {
            console.error("No se pudo iniciar la sesión de evaluación", evaluationError);
        }
    };

    const finishEvaluation = async () => {
        if (!evaluationSession) return;
        try {
            await recordEvaluationEvent("task_completed", activeTab, { completed: true });
            await api.post(`/evaluation/sessions/${evaluationSession.id}/finish`, { completed: true });
            localStorage.removeItem("mga_evaluation_session_id");
            setEvaluationSession(null);
        } catch (evaluationError) {
            console.error("No se pudo finalizar la sesión de evaluación", evaluationError);
        }
    };

    const renderContent = () => {
        switch (activeTab) {
            case MGASection.DEVELOPMENT_PLAN:
                return <DevelopmentPlan projectId={id} />;
            case MGASection.PROBLEM:
                // Dominio: Problemática | Técnica: Árbol de Problemas
                return (
                    <ProblemsTree
                        projectId={id}
                        projectName={project?.name}
                        ProjectDescription={project?.description}
                        suggestionApplication={suggestionApplication}
                    />
                );
            case MGASection.PARTICIPANTS:
                return <Participants projectId={id} />;
            case MGASection.POPULATION:
                return <Population projectId={id} />;
            case MGASection.OBJECTIVES:
                return <Objectives projectId={id} suggestionApplication={suggestionApplication} />;
            case MGASection.ALTERNATIVES:
                return <AlternativesGeneral projectId={id} />;
            case MGASection.REQUIREMENTS:
                return <RequirementsGeneral projectId={id} />;
            case MGASection.TECHNICAL_ANALYSIS:
                return <TechnicalAnalysis projectId={id} suggestionApplication={suggestionApplication} />;
            case MGASection.LOCALIZATION:
                return <LocalizationGeneral projectId={id} />;
            case MGASection.VALUE_CHAIN:
                return <ValueChain projectId={id} />;
            default:
                return <div>Componente no disponible</div>;
        }
    };

    return (
        <section className="formulation-route">
            <div className={`formulation-layout ${chatOpen ? "chat-open" : "chat-closed"}`}>
                <div className="formulation-main">
                    <div className="px-4 pt-3 formulation-header-surface">
                        <ProjectHeader id={id} project={project} loading={loading} error={error} />
                    </div>

                    <main className="formulation-main-body flex-grow-1 d-flex flex-column">
                        <nav className="formulation-tabs px-4 py-2 d-flex gap-2 flex-wrap" aria-label="Secciones de formulación MGA">
                            {sectionOrder.map((section) => (
                                <button
                                    key={section}
                                    className={`btn btn-sm ${activeTab === section ? "btn-primary" : "btn-outline-primary"}`}
                                    onClick={() => handleTabChange(section)}
                                    title={`Estado: ${sectionStates[section]?.status || "sin validar"}`}
                                >
                                    {MGA_SECTION_METADATA[section].label}
                                    {sectionStates[section]?.status === "COMPLETE" && <span aria-label="Completa"> ✓</span>}
                                    {sectionStates[section] && <small className="ms-1">{sectionStates[section].completion_percent}% ({sectionStates[section].required_fields_completed} de {sectionStates[section].required_fields_total} campos obligatorios)</small>}
                                </button>
                            ))}
                            <button className="btn btn-outline-success btn-sm" onClick={handleReview}>
                                <ClipboardCheck aria-hidden="true" size={16} /> Revisar formulación
                            </button>
                            {evaluationSession ? (
                                <button className="btn btn-outline-danger btn-sm" onClick={finishEvaluation}>Finalizar evaluación</button>
                            ) : (
                                <span className="d-inline-flex gap-1">
                                    <input className="form-control form-control-sm" aria-label="Identificador anónimo del participante" placeholder="ID evaluador" value={participantId} onChange={(event) => setParticipantId(event.target.value)} />
                                    <button className="btn btn-outline-secondary btn-sm" onClick={startEvaluation} disabled={!participantId.trim()}>Iniciar evaluación</button>
                                </span>
                            )}
                        </nav>

                        <section className="formulation-content p-4">
                            {renderContent()}
                            <p className="text-muted small mt-3"><span className="text-danger">*</span> Campo obligatorio</p>
                            <div className="formulation-section-actions">
                                <button
                                    className="btn btn-outline-primary"
                                    disabled={sectionOrder.indexOf(activeTab) === 0}
                                    onClick={() => handleTabChange(sectionOrder[sectionOrder.indexOf(activeTab) - 1])}
                                >
                                    <ChevronLeft aria-hidden="true" /> Anterior
                                </button>
                                {sectionOrder.indexOf(activeTab) < sectionOrder.length - 1 && (
                                    <button
                                        className="btn btn-primary"
                                        onClick={() => handleTabChange(sectionOrder[sectionOrder.indexOf(activeTab) + 1])}
                                    >
                                        Siguiente <ChevronRight aria-hidden="true" />
                                    </button>
                                )}
                            </div>
                        </section>
                    </main>
                </div>

                <div className={`formulation-chat-panel ${chatOpen ? "open" : "closed"}`}>

                    <button
                        className="chat-toggle-btn"
                        onClick={toggleChat}
                        title={chatOpen ? "Ocultar asistente IA" : "Mostrar asistente IA"}
                    >
                        {chatOpen ? "❯❯" : "❮❮"}
                    </button>

                    {chatOpen && (
                        <Chatbot
                            projectId={id}
                            activeTab={activeTab}
                            evaluationSessionId={evaluationSession?.id}
                            onApplySuggestedChanges={applySuggestedChanges}
                        />
                    )}

                </div>
            </div>
            <SectionValidationModal
                validation={validationModal}
                sectionName={validationModal ? MGA_SECTION_METADATA[validationModal.tab]?.label : ""}
                onClose={() => setValidationModal(null)}
            />
            {review && (
                <div className="section-validation-backdrop" role="presentation" onMouseDown={() => setReview(null)}>
                    <section className="section-validation-modal" role="dialog" aria-modal="true" onMouseDown={(event) => event.stopPropagation()}>
                        <header><ClipboardCheck aria-hidden="true" /><h2>Revisión de formulación: {review.status}</h2></header>
                        <ul>{review.sections.map((item) => <li key={item.section}>{MGA_SECTION_METADATA[MGA_VALIDATION_SECTION_TO_TAB[item.section]]?.label}: {item.complete ? "CORRECTO" : `${item.completion_percent}%`} ({item.required_fields_completed} de {item.required_fields_total} campos obligatorios)</li>)}</ul>
                        <ul>{review.findings.filter((item) => item.severity !== "CORRECTO").map((item, index) => <li key={`${item.section}-${index}`}><button className="btn btn-link p-0" onClick={() => { setReview(null); handleTabChange(MGA_VALIDATION_SECTION_TO_TAB[item.section]); }}>{item.severity}: {item.description}</button></li>)}</ul>
                        <footer><button className="btn btn-outline-secondary" onClick={() => setReview(null)}>Cerrar</button></footer>
                    </section>
                </div>
            )}
        </section>
    );
}

export default Formulation;
