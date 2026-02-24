/**
 * Constantes de la aplicación
 */

export const APP_CONFIG = {
    API_BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
    API_TIMEOUT: 30000,
    MAX_RETRIES: 3,
    TOKEN_STORAGE_KEY: 'auth_token',
    PROJECT_STORAGE_KEY: 'current_project_id',
};

export const TABS = {
    PROBLEMS: 'problems',
    PARTICIPANTS: 'participants_general',
    POPULATION: 'population',
    OBJECTIVES: 'objectives',
    ALTERNATIVES: 'alternatives',
} as const;

export const PROJECT_STATUS = {
    DRAFT: 'draft',
    ACTIVE: 'active',
    COMPLETED: 'completed',
} as const;

export const POPULATION_TYPES = {
    AFFECTED: 'affected',
    INTERVENTION: 'intervention',
} as const;

export const MGA_STAGES = [
    { id: 'problems', label: 'Árbol de Problemas', icon: '🌳' },
    { id: 'participants_general', label: 'Participantes', icon: '👥' },
    { id: 'population', label: 'Población', icon: '👨‍👩‍👧‍👦' },
    { id: 'objectives', label: 'Objetivos', icon: '🎯' },
    { id: 'alternatives', label: 'Alternativas', icon: '💡' },
];

export const PAGINATION = {
    DEFAULT_PAGE_SIZE: 10,
    MAX_PAGE_SIZE: 100,
};
