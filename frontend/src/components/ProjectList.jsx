import { useContext, useEffect } from "react";
import { ProjectContext } from "../context/ProjectContext";
import { Link } from "react-router-dom";
import api from "../services/api";
import { useNotification } from "../context/NotificationContext";

function ProjectList() {
    const { projects, setProjects, deleteProject } = useContext(ProjectContext);
    const { showSuccess, showError, showConfirmation } = useNotification();

    useEffect(() => {
        const fetchProjects = async () => {
            try {
                const response = await api.get("/projects/");
                setProjects(response.data);
            } catch (error) {
                console.error("Error fetching projects:", error);
            }
        };

        fetchProjects();
    }, [setProjects]);

    const handleDelete = async (id) => {
        const confirmed = await showConfirmation({
            title: "Eliminar Proyecto",
            message: "¿Está seguro de que desea eliminar este proyecto?"
        });
        if (confirmed) {
            try {
                await deleteProject(id);
                showSuccess("Proyecto eliminado correctamente.");
            } catch {
                showError("Error al eliminar el proyecto.");
            }
        }
    };

    return (
        <section className="app-page container mt-4">
            <h2 className="app-page-title">Proyectos</h2>
            <p className="app-page-subtitle">
                Gestione los proyectos registrados en la plataforma MGA IA.
            </p>

            <Link to="/create-project" className="btn btn-success btn-sm mb-3">
                Crear Proyecto
            </Link>

            <div className="table-responsive">
                <table className="table table-striped table-bordered">
                    <thead className="table-dark">
                        <tr>
                            <th>ID</th>
                            <th>Nombre</th>
                            <th>Descripción</th>
                            <th>Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        {projects.map((project) => (
                            <tr key={project.id}>
                                <td>{project.id}</td>
                                <td>{project.name}</td>
                                <td>{project.description}</td>
                                <td>
                                    <Link to={`/edit-project/${project.id}`} className="btn btn-sm btn-primary me-2">
                                        Editar
                                    </Link>
                                    <button className="btn btn-sm btn-danger" onClick={() => handleDelete(project.id)}>
                                        Eliminar
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </section>
    );
}

export default ProjectList;
