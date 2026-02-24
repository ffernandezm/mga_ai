/**
 * Hook personalizado para gestionar datos de proyecto
 * Proporciona acceso centralizando a datos del proyecto actual
 */

import { useState, useCallback, useEffect } from 'react';
import projectService from '../services/projectService';
import { Project, ProblemTree, Participant, Population, Objective, Alternative } from '../types';
import { ErrorHandler } from '../services/errorHandler';

export function useProjectData(projectId?: string | number) {
    const [project, setProject] = useState<Project | null>(null);
    const [problemTree, setProblemTree] = useState<ProblemTree | null>(null);
    const [participants, setParticipants] = useState<Participant[]>([]);
    const [populations, setPopulations] = useState<Population[]>([]);
    const [objectives, setObjectives] = useState<Objective[]>([]);
    const [alternatives, setAlternatives] = useState<Alternative[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Cargar proyecto
    const loadProject = useCallback(async () => {
        if (!projectId) return;

        try {
            setLoading(true);
            setError(null);
            const data = await projectService.getProject(projectId);
            setProject(data);
        } catch (err) {
            const apiError = ErrorHandler.normalize(err);
            const errorMsg = ErrorHandler.getUserMessage(apiError);
            setError(errorMsg);
            ErrorHandler.log(apiError, 'useProjectData.loadProject');
        } finally {
            setLoading(false);
        }
    }, [projectId]);

    // Cargar árbol de problemas
    const loadProblemTree = useCallback(async () => {
        if (!projectId) return;

        try {
            const data = await projectService.getProblemTree(projectId);
            setProblemTree(data);
        } catch (err) {
            const apiError = ErrorHandler.normalize(err);
            ErrorHandler.log(apiError, 'useProjectData.loadProblemTree');
        }
    }, [projectId]);

    // Cargar participantes
    const loadParticipants = useCallback(async () => {
        if (!projectId) return;

        try {
            const data = await projectService.getParticipants(projectId);
            setParticipants(data);
        } catch (err) {
            const apiError = ErrorHandler.normalize(err);
            ErrorHandler.log(apiError, 'useProjectData.loadParticipants');
        }
    }, [projectId]);

    // Cargar poblaciones
    const loadPopulations = useCallback(async () => {
        if (!projectId) return;

        try {
            const data = await projectService.getPopulations(projectId);
            setPopulations(data);
        } catch (err) {
            const apiError = ErrorHandler.normalize(err);
            ErrorHandler.log(apiError, 'useProjectData.loadPopulations');
        }
    }, [projectId]);

    // Cargar objetivos
    const loadObjectives = useCallback(async () => {
        if (!projectId) return;

        try {
            const data = await projectService.getObjectives(projectId);
            setObjectives(data);
        } catch (err) {
            const apiError = ErrorHandler.normalize(err);
            ErrorHandler.log(apiError, 'useProjectData.loadObjectives');
        }
    }, [projectId]);

    // Cargar alternativas
    const loadAlternatives = useCallback(async () => {
        if (!projectId) return;

        try {
            const data = await projectService.getAlternatives(projectId);
            setAlternatives(data);
        } catch (err) {
            const apiError = ErrorHandler.normalize(err);
            ErrorHandler.log(apiError, 'useProjectData.loadAlternatives');
        }
    }, [projectId]);

    // Cargar todo
    const loadAllData = useCallback(async () => {
        setLoading(true);
        await Promise.all([
            loadProject(),
            loadProblemTree(),
            loadParticipants(),
            loadPopulations(),
            loadObjectives(),
            loadAlternatives(),
        ]);
        setLoading(false);
    }, [
        loadProject,
        loadProblemTree,
        loadParticipants,
        loadPopulations,
        loadObjectives,
        loadAlternatives,
    ]);

    // Cargar al inicializar
    useEffect(() => {
        if (projectId) {
            loadProject();
        }
    }, [projectId, loadProject]);

    return {
        project,
        problemTree,
        participants,
        populations,
        objectives,
        alternatives,
        loading,
        error,
        loadProject,
        loadProblemTree,
        loadParticipants,
        loadPopulations,
        loadObjectives,
        loadAlternatives,
        loadAllData,
    };
}
