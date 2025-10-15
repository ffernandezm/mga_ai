import React, { useEffect, useState } from 'react';
import ProjectForm from './ProjectForm';
import api from '../services/api';

const ProjectList = () => {
  const [Projects, setProjects] = useState([]);

  const fetchProjects = async () => {
    try {
      const response = await api.get('/projects');
      setProjects(response.data.projects);
    } catch (error) {
      console.error("Error fetching Projects", error);
    }
  };

  const addProject = async (projectName) => {
    try {
      await api.post('/projects', { name: projectName });
      fetchProjects();  // Refresh the list after adding a project
    } catch (error) {
      console.error("Error adding project", error);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  return (
    <div>
      <h2>Lista de Proyectos</h2>
      <ul>
        {projects.map((project, index) => (
          <li key={index}>{project.name}</li>
        ))}
      </ul>
      <ProjectForm addProject={addProject} />
    </div>
  );
};

export default ProjectList;