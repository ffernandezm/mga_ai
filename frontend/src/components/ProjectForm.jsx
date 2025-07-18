import { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../services/api";

import ProblemsTree from "./ProblemsTree";
import Chatbot from "./Chatbot";
import "../styles/ProjectForm.css"; // Asegúrate de crear este archivo para estilos

function ProjectForm() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [project, setProject] = useState({ name: "", description: "" });

    useEffect(() => {
        if (id) {
            const fetchProject = async () => {
                try {
                    const response = await api.get(`/projects/${id}`);
                    setProject(response.data);
                } catch (error) {
                    console.error("Error fetching project:", error);
                }
            };
            fetchProject();
        }
    }, [id]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!project.name.trim() || !project.description.trim()) return;

        try {
            if (id) {
                await api.put(`/projects/${id}`, project);
            } else {
                await api.post("/projects/", project);
            }
            navigate("/projects");
        } catch (error) {
            console.error("Error saving project", error);
        }
    };

    return (
        <div className="project-container">
            <h2>{id ? "Edit Project" : "Create Project"}</h2>

            <div className="content-wrapper">
                <Chatbot projectId={project.id} />
                <ProblemsTree projectId={project.id} projectName={project.name} ProjectDescription={project.description} />
            </div>

            <button type="button" className="btn-secondary" onClick={() => navigate("/projects")}>
                Regresar a Proyectos
            </button>
        </div>
    );
}

export default ProjectForm;
