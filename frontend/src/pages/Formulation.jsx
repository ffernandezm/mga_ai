import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom"; // 👈 Agregamos useNavigate

import ProblemsTree from "../components/ProblemsTree";
import Participants from "../components/Participants";
import Population from "../components/Population";
import Objectives from "../components/Objectives";
import AlternativesGeneral from "../components/AlternativesGeneral";
import Chatbot from "../components/Chatbot";
import ProjectHeader from "../components/ProjectHeader";

import api from "../services/api";

function Formulation() {
    const { id } = useParams();
    const navigate = useNavigate(); // 👈 Hook para redirigir

    const [activeTab, setActiveTab] = useState("problems");
    const [project, setProject] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

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

    const renderContent = () => {
        switch (activeTab) {
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
            case "alternatives":
                return <AlternativesGeneral projectId={id} />;
            default:
                return <div>Componente no disponible</div>;
        }
    };

    return (
        <div className="d-flex" style={{ height: "100vh", overflow: "hidden" }}>
            {/* Columna izquierda */}
            <div className="flex-grow-1 d-flex flex-column overflow-auto">
                <div className="px-4 pt-3">
                    <ProjectHeader id={id} project={project} loading={loading} error={error} />

                    <div className="text-end mt-3">
                        <button
                            className="btn btn-success"
                            onClick={() => navigate(`/projects/${id}/survey`)}
                        >
                            📝 Ir a la Encuesta del Proyecto
                        </button>
                    </div>
                </div>

                <main className="flex-grow-1 d-flex flex-column overflow-auto">
                    {/* Barra de navegación */}
                    <nav className="bg-white border-bottom px-4 py-2 d-flex gap-3 flex-wrap">
                        <button
                            className={`btn btn-sm ${activeTab === "problems" ? "btn-primary" : "btn-outline-primary"
                                }`}
                            onClick={() => setActiveTab("problems")}
                        >
                            Árbol de Problemas
                        </button>
                        <button
                            className={`btn btn-sm ${activeTab === "participants_general"
                                ? "btn-primary"
                                : "btn-outline-primary"
                                }`}
                            onClick={() => setActiveTab("participants_general")}
                        >
                            Participantes
                        </button>
                        <button
                            className={`btn btn-sm ${activeTab === "population"
                                ? "btn-primary"
                                : "btn-outline-primary"
                                }`}
                            onClick={() => setActiveTab("population")}
                        >
                            Población
                        </button>
                        <button
                            className={`btn btn-sm ${activeTab === "objectives"
                                ? "btn-primary"
                                : "btn-outline-primary"
                                }`}
                            onClick={() => setActiveTab("objectives")}
                        >
                            Objetivos
                        </button>
                        <button
                            className={`btn btn-sm ${activeTab === "alternatives"
                                ? "btn-primary"
                                : "btn-outline-primary"
                                }`}
                            onClick={() => setActiveTab("alternatives")}
                        >
                            Alternativas
                        </button>
                    </nav>

                    <section className="p-4 overflow-auto" style={{ flex: 1 }}>
                        {renderContent()}
                    </section>
                </main>
            </div>

            {/* Columna derecha con chatbot sticky */}
            <div
                style={{
                    width: "350px",
                    height: "100vh",
                    background: "#f9f9f9",
                    borderLeft: "1px solid #ddd",
                    padding: "1rem",
                    boxSizing: "border-box",
                }}
            >
                <Chatbot projectId={id} activeTab={activeTab} />
            </div>
        </div>
    );
}

export default Formulation;
