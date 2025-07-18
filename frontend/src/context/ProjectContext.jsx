import { createContext, useState } from "react";
import api from "../services/api";

export const ProjectContext = createContext();

export function ProjectProvider({ children }) {
  const [projects, setProjects] = useState([]);

  const addProject = (project) => {
    setProjects([...projects, { id: Date.now(), ...project }]);
  };

  const deleteProject = async (id) => {
    try {
      await api.delete(`/projects/${id}`); // Llamada al backend para eliminar el proyecto
      setProjects((prevProjects) => prevProjects.filter((project) => project.id !== id)); // Actualizar el estado local
    } catch (error) {
      console.error("Error deleting project:", error);
    }
  };

  return (
    <ProjectContext.Provider value={{ projects, setProjects, addProject, deleteProject }}>
      {children}
    </ProjectContext.Provider>
  );
}