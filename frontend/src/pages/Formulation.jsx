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

function Formulation() {
    const { id } = useParams();
    const navigate = useNavigate();
    const location = useLocation(); // 👈 Para leer query params

    const [activeTab, setActiveTab] = useState("development_plans");
    const [project, setProject] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

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

    const handleTabChange = (tab) => {
        setActiveTab(tab);
        // 👇 Actualiza la URL sin recargar la página
        navigate(`/projects/${id}/formulation?tab=${tab}`, { replace: true });
    };

    const renderContent = () => {
        switch (activeTab) {
            case "development_plans":
                return <DevelopmentPlan projectId={id} />;
            case "problems":
                return (
                    <ProblemsTree
                        projectId={id}
                        projectName={project?.name}
                        ProjectDescription={project?.description}
                    />
                );
            case "participants_general":
                return <Participants projectId={id} />;
            case "population":
                return <Population projectId={id} />;
            case "objectives":
                return <Objectives projectId={id} />;
            case "alternatives_general":
                return <AlternativesGeneral projectId={id} />;
            case "requirements_general":
                return <RequirementsGeneral projectId={id} />;
            case "technical_analysis":
                return <TechnicalAnalysis projectId={id} />;
            case "localization_general":
                return <LocalizationGeneral projectId={id} />;
            case "value_chain":
                return <ValueChain projectId={id} />;
            default:
                return <div>Componente no disponible</div>;
        }
    };

    return (
        <div className="d-flex" style={{ height: "100vh", overflow: "hidden" }}>
            {/* Columna izquierda */}
            <div className="flex-grow-1 d-flex flex-column overflow-auto">
                <div className="px-4 pt-3">
                    <div className="text-end mt-3">
                        <button
                            className="btn btn-success"
                            onClick={() => navigate(`/projects/${id}/survey`)}
                        >
                            📝 Ir a la encuesta
                        </button>
                    </div>
                    <ProjectHeader id={id} project={project} loading={loading} error={error} />
                </div>

                <main className="flex-grow-1 d-flex flex-column overflow-auto">
                    {/* Barra de navegación */}
                    <nav className="bg-white border-bottom px-4 py-2 d-flex gap-3 flex-wrap">
                        <button
                            className={`btn btn-sm ${activeTab === "development_plans" ? "btn-primary" : "btn-outline-primary"
                                }`}
                            onClick={() => handleTabChange("development_plans")}
                        >
                            Plan de Desarrollo
                        </button>
                        <button
                            className={`btn btn-sm ${activeTab === "problems" ? "btn-primary" : "btn-outline-primary"
                                }`}
                            onClick={() => handleTabChange("problems")}
                        >
                            Árbol de Problemas
                        </button>
                        <button
                            className={`btn btn-sm ${activeTab === "participants_general"
                                ? "btn-primary"
                                : "btn-outline-primary"
                                }`}
                            onClick={() => handleTabChange("participants_general")}
                        >
                            Participantes
                        </button>
                        <button
                            className={`btn btn-sm ${activeTab === "population" ? "btn-primary" : "btn-outline-primary"
                                }`}
                            onClick={() => handleTabChange("population")}
                        >
                            Población
                        </button>
                        <button
                            className={`btn btn-sm ${activeTab === "objectives" ? "btn-primary" : "btn-outline-primary"
                                }`}
                            onClick={() => handleTabChange("objectives")}
                        >
                            Objetivos
                        </button>
                        <button
                            className={`btn btn-sm ${activeTab === "alternatives_general" ? "btn-primary" : "btn-outline-primary"
                                }`}
                            onClick={() => handleTabChange("alternatives_general")}
                        >
                            Alternativas
                        </button>
                    </nav>
                    <nav className="bg-white border-bottom px-4 py-2 d-flex gap-3 flex-wrap">
                        <button
                            className={`btn btn-sm ${activeTab === "requirements_general" ? "btn-primary" : "btn-outline-primary"
                                }`}
                            onClick={() => handleTabChange("requirements_general")}
                        >
                            Necesidades
                        </button>
                        <button
                            className={`btn btn-sm ${activeTab === "technical_analysis"
                                ? "btn-primary"
                                : "btn-outline-primary"
                                }`}
                            onClick={() => handleTabChange("technical_analysis")}
                        >
                            Análisis Técnico
                        </button>
                        <button
                            className={`btn btn-sm ${activeTab === "localization_general" ? "btn-primary" : "btn-outline-primary"
                                }`}
                            onClick={() => handleTabChange("localization_general")}
                        >
                            Localización
                        </button>

                        {/* Aqui cambiar a la nueva tab que se llamará value_chain */}
                        <button
                            className={`btn btn-sm ${activeTab === "value_chain" ? "btn-primary" : "btn-outline-primary"
                                }`}
                            onClick={() => handleTabChange("value_chain")}
                        >
                            Cadeba de Valor
                        </button>
                    </nav>

                    <section className="p-4 overflow-auto" style={{ flex: 1 }}>
                        {renderContent()}
                    </section>
                </main>
            </div>

            <div
            // style={{
            //     width: "600px",
            //     height: "100vh",
            //     background: "#f9f9f9",
            //     borderLeft: "1px solid #ddd",
            //     padding: "1rem",
            //     boxSizing: "border-box",
            // }}
            >
                <Chatbot projectId={id} activeTab={activeTab} />
            </div>
        </div>
    );
}

export default Formulation;
