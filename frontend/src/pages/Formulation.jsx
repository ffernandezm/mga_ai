import { useState, useEffect } from "react";
import { useParams, useNavigate, useLocation } from "react-router-dom";
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
import api from "../services/api";
import { MGASection, MGA_SECTION_METADATA } from "../utils/constants";
import "./Formulation.css";

function Formulation() {
    const { id } = useParams();
    const navigate = useNavigate();
    const location = useLocation(); // 👈 Para leer query params

    const [activeTab, setActiveTab] = useState("development_plans");
    const [project, setProject] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const [chatOpen, setChatOpen] = useState(() => {
        const savedState = localStorage.getItem("mga_chat_open");

        return savedState !== null
            ? JSON.parse(savedState)
            : true;
    });

    // 👇 Detectar el parámetro ?tab= en la URL
    useEffect(() => {
        const params = new URLSearchParams(location.search);
        const tab = params.get("tab");
        if (tab) {
            setActiveTab(tab);
        }
    }, [location.search]);

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

    const handleTabChange = (tab) => {
        setActiveTab(tab);
        // 👇 Actualiza la URL sin recargar la página
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
                        {/* Barra de navegación */}
                        <nav className="formulation-tabs px-4 py-2 d-flex gap-3 flex-wrap">
                            <button
                                className={`btn btn-sm ${activeTab === MGASection.DEVELOPMENT_PLAN ? "btn-primary" : "btn-outline-primary"
                                    }`}
                                onClick={() => handleTabChange(MGASection.DEVELOPMENT_PLAN)}
                            >
                                {MGA_SECTION_METADATA[MGASection.DEVELOPMENT_PLAN].label}
                            </button>
                            <button
                                className={`btn btn-sm ${activeTab === MGASection.PROBLEM ? "btn-primary" : "btn-outline-primary"
                                    }`}
                                onClick={() => handleTabChange(MGASection.PROBLEM)}
                                title={`Técnica MGA: ${MGA_SECTION_METADATA[MGASection.PROBLEM].technique}`}
                            >
                                {MGA_SECTION_METADATA[MGASection.PROBLEM].label}
                            </button>
                            <button
                                className={`btn btn-sm ${activeTab === MGASection.PARTICIPANTS
                                    ? "btn-primary"
                                    : "btn-outline-primary"
                                    }`}
                                onClick={() => handleTabChange(MGASection.PARTICIPANTS)}
                            >
                                {MGA_SECTION_METADATA[MGASection.PARTICIPANTS].label}
                            </button>
                            <button
                                className={`btn btn-sm ${activeTab === MGASection.POPULATION ? "btn-primary" : "btn-outline-primary"
                                    }`}
                                onClick={() => handleTabChange(MGASection.POPULATION)}
                            >
                                {MGA_SECTION_METADATA[MGASection.POPULATION].label}
                            </button>
                            <button
                                className={`btn btn-sm ${activeTab === MGASection.OBJECTIVES ? "btn-primary" : "btn-outline-primary"
                                    }`}
                                onClick={() => handleTabChange(MGASection.OBJECTIVES)}
                            >
                                {MGA_SECTION_METADATA[MGASection.OBJECTIVES].label}
                            </button>
                            <button
                                className={`btn btn-sm ${activeTab === MGASection.ALTERNATIVES ? "btn-primary" : "btn-outline-primary"
                                    }`}
                                onClick={() => handleTabChange(MGASection.ALTERNATIVES)}
                            >
                                {MGA_SECTION_METADATA[MGASection.ALTERNATIVES].label}
                            </button>
                        </nav>
                        <nav className="formulation-tabs px-4 py-2 d-flex gap-3 flex-wrap">
                            <button
                                className={`btn btn-sm ${activeTab === MGASection.REQUIREMENTS ? "btn-primary" : "btn-outline-primary"
                                    }`}
                                onClick={() => handleTabChange(MGASection.REQUIREMENTS)}
                            >
                                {MGA_SECTION_METADATA[MGASection.REQUIREMENTS].label}
                            </button>
                            <button
                                className={`btn btn-sm ${activeTab === MGASection.TECHNICAL_ANALYSIS
                                    ? "btn-primary"
                                    : "btn-outline-primary"
                                    }`}
                                onClick={() => handleTabChange(MGASection.TECHNICAL_ANALYSIS)}
                            >
                                {MGA_SECTION_METADATA[MGASection.TECHNICAL_ANALYSIS].label}
                            </button>
                            <button
                                className={`btn btn-sm ${activeTab === MGASection.LOCALIZATION ? "btn-primary" : "btn-outline-primary"
                                    }`}
                                onClick={() => handleTabChange(MGASection.LOCALIZATION)}
                            >
                                {MGA_SECTION_METADATA[MGASection.LOCALIZATION].label}
                            </button>

                            <button
                                className={`btn btn-sm ${activeTab === MGASection.VALUE_CHAIN ? "btn-primary" : "btn-outline-primary"
                                    }`}
                                onClick={() => handleTabChange(MGASection.VALUE_CHAIN)}
                            >
                                {MGA_SECTION_METADATA[MGASection.VALUE_CHAIN].label}
                            </button>
                        </nav>

                        <section className="formulation-content p-4">
                            {renderContent()}
                        </section>
                    </main>
                </div>

                <div className={`formulation-chat-panel ${chatOpen ? "open" : "closed"}`}>

                    <button
                        className="chat-toggle-btn"
                        onClick={toggleChat}
                        title={chatOpen ? "Ocultar asistente IA" : "Mostrar asistente IA"}
                    >
                        {chatOpen ? "❯" : "❮"}
                    </button>

                    {chatOpen && (
                        <Chatbot
                            projectId={id}
                            activeTab={activeTab}
                        />
                    )}

                </div>
            </div>
        </section>
    );
}

export default Formulation;
