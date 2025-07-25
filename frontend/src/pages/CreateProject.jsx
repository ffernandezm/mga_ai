import { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../services/api";
import "../styles/ProjectForm.css"; // Asegúrate de crear este archivo para estilos

function CreateProject() {
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

            <form onSubmit={handleSubmit} className="project-form">
                <div className="form-group">
                    <label>Project Name</label>
                    <input
                        type="text"
                        value={project.name}
                        onChange={(e) => setProject({ ...project, name: e.target.value })}
                    />
                </div>
                <div className="form-group">
                    <label>Description</label>
                    <textarea
                        value={project.description}
                        onChange={(e) => setProject({ ...project, description: e.target.value })}
                    />
                </div>
                <button type="submit" className="btn-primary">
                    {id ? "Update Project" : "Add Project"}
                </button>
            </form>

            <button type="button" className="btn-secondary" onClick={() => navigate("/projects")}>
                Regresar a Proyectos
            </button>
        </div>
    );
}

export default CreateProject;
