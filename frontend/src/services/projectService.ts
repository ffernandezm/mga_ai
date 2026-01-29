/**
 * Servicio para gestionar Proyectos
 * Centraliza todas las operaciones CRUD de proyectos
 */

import apiService from './api';
import { Project, ProblemTree, Participant, Population, Objective, Alternative } from '../types';

class ProjectService {
    /**
     * Obtener todos los proyectos
     */
    async getAllProjects(): Promise<Project[]> {
        return apiService.get<Project[]>('/projects');
    }

    /**
     * Obtener un proyecto por ID
     */
    async getProject(id: string | number): Promise<Project> {
        return apiService.get<Project>(`/projects/${id}`);
    }

    /**
     * Crear un nuevo proyecto
     */
    async createProject(data: Omit<Project, 'id'>): Promise<Project> {
        return apiService.post<Project>('/projects', data);
    }

    /**
     * Actualizar un proyecto
     */
    async updateProject(id: string | number, data: Partial<Project>): Promise<Project> {
        return apiService.put<Project>(`/projects/${id}`, data);
    }

    /**
     * Eliminar un proyecto
     */
    async deleteProject(id: string | number): Promise<void> {
        await apiService.delete(`/projects/${id}`);
    }

    // ========== ÁRBOL DE PROBLEMAS ==========

    async getProblemTree(projectId: string | number): Promise<ProblemTree> {
        return apiService.get<ProblemTree>(`/problems/${projectId}`);
    }

    async saveProblemTree(projectId: string | number, data: ProblemTree): Promise<ProblemTree> {
        return apiService.post<ProblemTree>(`/problems/${projectId}`, data);
    }

    async updateProblemTree(projectId: string | number, data: ProblemTree): Promise<ProblemTree> {
        return apiService.put<ProblemTree>(`/problems/${projectId}`, data);
    }

    // ========== PARTICIPANTES ==========

    async getParticipants(projectId: string | number): Promise<Participant[]> {
        return apiService.get<Participant[]>(`/participants/${projectId}`);
    }

    async createParticipant(data: Participant): Promise<Participant> {
        return apiService.post<Participant>('/participants', data);
    }

    async updateParticipant(id: string | number, data: Partial<Participant>): Promise<Participant> {
        return apiService.put<Participant>(`/participants/${id}`, data);
    }

    async deleteParticipant(id: string | number): Promise<void> {
        await apiService.delete(`/participants/${id}`);
    }

    // ========== POBLACIONES ==========

    async getPopulations(projectId: string | number): Promise<Population[]> {
        return apiService.get<Population[]>(`/populations/${projectId}`);
    }

    async createPopulation(data: Population): Promise<Population> {
        return apiService.post<Population>('/populations', data);
    }

    async updatePopulation(id: string | number, data: Partial<Population>): Promise<Population> {
        return apiService.put<Population>(`/populations/${id}`, data);
    }

    async deletePopulation(id: string | number): Promise<void> {
        await apiService.delete(`/populations/${id}`);
    }

    // ========== OBJETIVOS ==========

    async getObjectives(projectId: string | number): Promise<Objective[]> {
        return apiService.get<Objective[]>(`/objectives/${projectId}`);
    }

    async createObjective(data: Objective): Promise<Objective> {
        return apiService.post<Objective>('/objectives', data);
    }

    async updateObjective(projectId: string | number, id: string | number, data: Partial<Objective>): Promise<Objective> {
        return apiService.put<Objective>(`/objectives/${projectId}/${id}`, data);
    }

    async deleteObjective(id: string | number): Promise<void> {
        await apiService.delete(`/objectives/${id}`);
    }

    // ========== ALTERNATIVAS ==========

    async getAlternatives(projectId: string | number): Promise<Alternative[]> {
        return apiService.get<Alternative[]>(`/alternatives/${projectId}`);
    }

    async createAlternative(data: Alternative): Promise<Alternative> {
        return apiService.post<Alternative>('/alternatives', data);
    }

    async updateAlternative(id: string | number, data: Partial<Alternative>): Promise<Alternative> {
        return apiService.put<Alternative>(`/alternatives/${id}`, data);
    }

    async deleteAlternative(id: string | number): Promise<void> {
        await apiService.delete(`/alternatives/${id}`);
    }
}

export default new ProjectService();
