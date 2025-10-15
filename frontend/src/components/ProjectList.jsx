import { useContext, useEffect } from "react";
import { ProjectContext } from "../context/ProjectContext";
import { Link } from "react-router-dom";
import api from "../services/api";

function ProjectList() {
    const { projects, setProjects, deleteProject } = useContext(ProjectContext);

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

    return (
        <div className="container mt-4">
            <h2 className="mb-3">Projects</h2>
            <Link to="/create-project" className="btn btn-success mb-3">
                Crear Proyecto
            </Link>

            <div className="table-responsive">
                <table className="table table-striped table-bordered">
                    <thead className="table-dark">
                        <tr>
                            <th>ID</th>
                            <th>Name</th>
                            <th>Description</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {projects.map((project) => (
                            <tr key={project.id}>
                                <td>{project.id}</td>
                                <td>{project.name}</td>
                                <td>{project.description}</td>
                                <td>
                                    <Link to={`/edit-project/${project.id}`} className="btn btn-warning me-2">
                                        Edit
                                    </Link>
                                    <button className="btn btn-danger" onClick={() => deleteProject(project.id)}>
                                        Delete
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

export default ProjectList;
