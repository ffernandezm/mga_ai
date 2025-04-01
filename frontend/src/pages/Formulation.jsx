import { useState } from "react";
import ProjectForm from "../components/ProjectForm";
import ProblemsTree from "../components/ProblemsTree";
import Chatbot from "../components/Chatbot";
import { useParams } from "react-router-dom";

function Formulation() {
    const { id } = useParams(); // Obtener el ID del proyecto desde la URL
    const [selectedTab, setSelectedTab] = useState("project");

    return (
        <div className="d-flex vh-100">
            {/* Barra de navegación lateral */}
            <nav className="bg-light p-3 border-end" style={{ width: "250px" }}>
                <h4 className="mb-4">Formulación</h4>
                <ul className="nav flex-column">
                    <li className="nav-item">
                        <button
                            className={`nav-link w-100 text-start ${selectedTab === "project" ? "active bg-primary text-white" : ""}`}
                            onClick={() => setSelectedTab("project")}
                        >
                            Proyecto
                        </button>
                    </li>
                    <li className="nav-item">
                        <button
                            className={`nav-link w-100 text-start ${selectedTab === "problems" ? "active bg-primary text-white" : ""}`}
                            onClick={() => setSelectedTab("problems")}
                        >
                            Árbol de Problemas
                        </button>
                    </li>
                </ul>
            </nav>

            {/* Contenedor principal con chatbot y árbol de problemas */}
            <div className="d-flex flex-grow-1">
                {/* Chatbot a la izquierda */}
                <div className="p-3 border-end" style={{ width: "300px" }}>
                    <Chatbot />
                </div>

                {/* Contenido dinámico */}
                <div className="flex-grow-1 p-4">
                    {selectedTab === "project" ? <ProjectForm /> : <ProblemsTree projectId={id} />}
                </div>
            </div>
        </div>
    );
}

export default Formulation;
