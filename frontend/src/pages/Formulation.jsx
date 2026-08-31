import { useState, useEffect } from "react";
import { useParams, useNavigate, useLocation } from "react-router-dom";
import { ChevronLeft, ChevronRight } from "lucide-react";
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
                const response = await api.get(`/projects/${id}/sections/validation`);
                const states = Object.fromEntries(response.data.map((item) => [MGA_VALIDATION_SECTION_TO_TAB[item.section], item]));
                setSectionStates(states);
                const targetIndex = sectionOrder.indexOf(tab);
                const blocker = response.data.find(
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
        localStorage.setItem(
            "mga_chat_open",
            JSON.stringify(chatOpen)
        );
    }, [chatOpen]);

    const toggleChat = () => {
        setChatOpen(previousState => !previousState);
    };

    const handleTabChange = async (tab) => {
        const currentIndex = sectionOrder.indexOf(activeTab);
        const targetIndex = sectionOrder.indexOf(tab);
        if (targetIndex > currentIndex) {
            try {
                const response = await api.get(`/projects/${id}/sections/validation`);
                const states = Object.fromEntries(response.data.map((item) => [MGA_VALIDATION_SECTION_TO_TAB[item.section], item]));
                setSectionStates(states);
                const blocker = response.data.find(
                    (item) => sectionOrder.indexOf(MGA_VALIDATION_SECTION_TO_TAB[item.section]) < targetIndex && !item.complete
                );
                if (blocker) {
                    setValidationModal({ ...blocker, tab: MGA_VALIDATION_SECTION_TO_TAB[blocker.section] });
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
                    />
                );
            case MGASection.PARTICIPANTS:
                return <Participants projectId={id} />;
            case MGASection.POPULATION:
                return <Population projectId={id} />;
            case MGASection.OBJECTIVES:
                return <Objectives projectId={id} />;
            case MGASection.ALTERNATIVES:
                return <AlternativesGeneral projectId={id} />;
            case MGASection.REQUIREMENTS:
                return <RequirementsGeneral projectId={id} />;
            case MGASection.TECHNICAL_ANALYSIS:
                return <TechnicalAnalysis projectId={id} />;
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
                                </button>
                            ))}
                        </nav>

                        <section className="formulation-content p-4">
                            {renderContent()}
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
                        />
                    )}

                </div>
            </div>
            <SectionValidationModal
                validation={validationModal}
                sectionName={validationModal ? MGA_SECTION_METADATA[validationModal.tab]?.label : ""}
                onClose={() => setValidationModal(null)}
            />
        </section>
    );
}

export default Formulation;
