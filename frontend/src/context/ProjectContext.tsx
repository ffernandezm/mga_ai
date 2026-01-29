/**
 * Context mejorado para gestión de Proyectos
 * Proporciona estado global centralizado y métodos para gestionar proyectos
 */

import React, { createContext, useReducer, useCallback } from 'react';
import { Project, ErrorResponse } from '../types';
import projectService from '../services/projectService';
import { ErrorHandler, ApiError } from '../services/errorHandler';

export interface ProjectContextType {
    projects: Project[];
    loading: boolean;
    error: ErrorResponse | null;
    currentProject: Project | null;

    // Acciones
    loadProjects: () => Promise<void>;
    loadProject: (id: string | number) => Promise<void>;
    createProject: (data: Omit<Project, 'id'>) => Promise<Project>;
    updateProject: (id: string | number, data: Partial<Project>) => Promise<void>;
    deleteProject: (id: string | number) => Promise<void>;
    setCurrentProject: (project: Project | null) => void;
    clearError: () => void;
}

export const ProjectContext = createContext<ProjectContextType | undefined>(undefined);

interface ProjectState {
    projects: Project[];
    currentProject: Project | null;
    loading: boolean;
    error: ErrorResponse | null;
}

type ProjectAction =
    | { type: 'SET_LOADING'; payload: boolean }
    | { type: 'SET_ERROR'; payload: ErrorResponse | null }
    | { type: 'SET_PROJECTS'; payload: Project[] }
    | { type: 'SET_CURRENT_PROJECT'; payload: Project | null }
    | { type: 'ADD_PROJECT'; payload: Project }
    | { type: 'UPDATE_PROJECT'; payload: Project }
    | { type: 'DELETE_PROJECT'; payload: string | number };

const initialState: ProjectState = {
    projects: [],
    currentProject: null,
    loading: false,
    error: null,
};

function projectReducer(state: ProjectState, action: ProjectAction): ProjectState {
    switch (action.type) {
        case 'SET_LOADING':
            return { ...state, loading: action.payload };

        case 'SET_ERROR':
            return { ...state, error: action.payload };

        case 'SET_PROJECTS':
            return { ...state, projects: action.payload };

        case 'SET_CURRENT_PROJECT':
            return { ...state, currentProject: action.payload };

        case 'ADD_PROJECT':
            return { ...state, projects: [...state.projects, action.payload] };

        case 'UPDATE_PROJECT':
            return {
                ...state,
                projects: state.projects.map((p) =>
                    p.id === action.payload.id ? action.payload : p
                ),
                currentProject:
                    state.currentProject?.id === action.payload.id
                        ? action.payload
                        : state.currentProject,
            };

        case 'DELETE_PROJECT':
            return {
                ...state,
                projects: state.projects.filter((p) => p.id !== action.payload),
                currentProject:
                    state.currentProject?.id === action.payload ? null : state.currentProject,
            };

        default:
            return state;
    }
}

export interface ProjectProviderProps {
    children: React.ReactNode;
}

export function ProjectProvider({ children }: ProjectProviderProps) {
    const [state, dispatch] = useReducer(projectReducer, initialState);

    const loadProjects = useCallback(async () => {
        try {
            dispatch({ type: 'SET_LOADING', payload: true });
            dispatch({ type: 'SET_ERROR', payload: null });

            const projects = await projectService.getAllProjects();
            dispatch({ type: 'SET_PROJECTS', payload: projects });
        } catch (err) {
            const apiError = ErrorHandler.normalize(err);
            ErrorHandler.log(apiError, 'ProjectContext.loadProjects');
            dispatch({ type: 'SET_ERROR', payload: apiError.toErrorResponse() });
        } finally {
            dispatch({ type: 'SET_LOADING', payload: false });
        }
    }, []);

    const loadProject = useCallback(async (id: string | number) => {
        try {
            dispatch({ type: 'SET_LOADING', payload: true });
            dispatch({ type: 'SET_ERROR', payload: null });

            const project = await projectService.getProject(id);
            dispatch({ type: 'SET_CURRENT_PROJECT', payload: project });
        } catch (err) {
            const apiError = ErrorHandler.normalize(err);
            ErrorHandler.log(apiError, 'ProjectContext.loadProject');
            dispatch({ type: 'SET_ERROR', payload: apiError.toErrorResponse() });
        } finally {
            dispatch({ type: 'SET_LOADING', payload: false });
        }
    }, []);

    const createProject = useCallback(async (data: Omit<Project, 'id'>) => {
        try {
            dispatch({ type: 'SET_ERROR', payload: null });
            const newProject = await projectService.createProject(data);
            dispatch({ type: 'ADD_PROJECT', payload: newProject });
            return newProject;
        } catch (err) {
            const apiError = ErrorHandler.normalize(err);
            ErrorHandler.log(apiError, 'ProjectContext.createProject');
            dispatch({ type: 'SET_ERROR', payload: apiError.toErrorResponse() });
            throw apiError;
        }
    }, []);

    const updateProject = useCallback(async (id: string | number, data: Partial<Project>) => {
        try {
            dispatch({ type: 'SET_ERROR', payload: null });
            const updated = await projectService.updateProject(id, data);
            dispatch({ type: 'UPDATE_PROJECT', payload: updated });
        } catch (err) {
            const apiError = ErrorHandler.normalize(err);
            ErrorHandler.log(apiError, 'ProjectContext.updateProject');
            dispatch({ type: 'SET_ERROR', payload: apiError.toErrorResponse() });
            throw apiError;
        }
    }, []);

    const deleteProject = useCallback(async (id: string | number) => {
        try {
            dispatch({ type: 'SET_ERROR', payload: null });
            await projectService.deleteProject(id);
            dispatch({ type: 'DELETE_PROJECT', payload: id });
        } catch (err) {
            const apiError = ErrorHandler.normalize(err);
            ErrorHandler.log(apiError, 'ProjectContext.deleteProject');
            dispatch({ type: 'SET_ERROR', payload: apiError.toErrorResponse() });
            throw apiError;
        }
    }, []);

    const setCurrentProject = useCallback((project: Project | null) => {
        dispatch({ type: 'SET_CURRENT_PROJECT', payload: project });
    }, []);

    const clearError = useCallback(() => {
        dispatch({ type: 'SET_ERROR', payload: null });
    }, []);

    const value: ProjectContextType = {
        projects: state.projects,
        loading: state.loading,
        error: state.error,
        currentProject: state.currentProject,
        loadProjects,
        loadProject,
        createProject,
        updateProject,
        deleteProject,
        setCurrentProject,
        clearError,
    };

    return (
        <ProjectContext.Provider value={value}>
            {children}
        </ProjectContext.Provider>
    );
}

/**
 * Hook para usar el contexto de proyectos
 */
export function useProjects(): ProjectContextType {
    const context = React.useContext(ProjectContext);
    if (!context) {
        throw new Error('useProjects debe ser usado dentro de ProjectProvider');
    }
    return context;
}
