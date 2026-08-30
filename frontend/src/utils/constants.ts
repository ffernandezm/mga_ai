import { MGASection } from '../types/project';

export { MGASection };

/**
 * Constantes de la aplicación
 */

export const APP_CONFIG = {
    API_BASE_URL:
        (import.meta.env.VITE_API_URL as string | undefined) ||
        'http://localhost:8000',
    API_TIMEOUT: 30000,
    MAX_RETRIES: 3,
    TOKEN_STORAGE_KEY: 'auth_token',
    PROJECT_STORAGE_KEY: 'current_project_id',
};

/**
 * Metadata de secciones MGA que separa explícitamente:
 * - Dominio: Concepto del Dominio MGA (ej: Problemática)
 * - Técnica: Técnica/Metodología MGA (ej: Árbol de Problemas)
 * - Interfaz: Etiqueta visible en la interfaz UI (ej: Problemática / Árbol de problemas)
 */
export interface MGASectionMetadata {
    id: MGASection;
    domain: string;
    technique: string;
    label: string;
    icon: string;
}

export const MGA_SECTION_METADATA: Record<MGASection, MGASectionMetadata> = {
    [MGASection.DEVELOPMENT_PLAN]: {
        id: MGASection.DEVELOPMENT_PLAN,
        domain: 'Plan de Desarrollo',
        technique: 'Alineación Estratégica y PND',
        label: 'Plan de Desarrollo',
        icon: '📋',
    },
    [MGASection.PROBLEM]: {
        id: MGASection.PROBLEM,
        domain: 'Problemática',
        technique: 'Árbol de Problemas',
        label: 'Problemática',
        icon: '🌳',
    },
    [MGASection.PARTICIPANTS]: {
        id: MGASection.PARTICIPANTS,
        domain: 'Participantes',
        technique: 'Matriz de Involucrados / Actores',
        label: 'Participantes',
        icon: '👥',
    },
    [MGASection.POPULATION]: {
        id: MGASection.POPULATION,
        domain: 'Población',
        technique: 'Identificación de Población Afectada y Objetivo',
        label: 'Población',
        icon: '👨‍👩‍👧‍👦',
    },
    [MGASection.OBJECTIVES]: {
        id: MGASection.OBJECTIVES,
        domain: 'Objetivos',
        technique: 'Árbol de Objetivos',
        label: 'Objetivos',
        icon: '🎯',
    },
    [MGASection.ALTERNATIVES]: {
        id: MGASection.ALTERNATIVES,
        domain: 'Alternativas',
        technique: 'Configuración y Selección de Alternativas',
        label: 'Alternativas',
        icon: '💡',
    },
    [MGASection.REQUIREMENTS]: {
        id: MGASection.REQUIREMENTS,
        domain: 'Necesidades',
        technique: 'Análisis de Necesidades y Demanda/Oferta',
        label: 'Necesidades',
        icon: '📌',
    },
    [MGASection.TECHNICAL_ANALYSIS]: {
        id: MGASection.TECHNICAL_ANALYSIS,
        domain: 'Análisis Técnico',
        technique: 'Estudio Técnico de Alternativas',
        label: 'Análisis Técnico',
        icon: '⚙️',
    },
    [MGASection.LOCALIZATION]: {
        id: MGASection.LOCALIZATION,
        domain: 'Localización',
        technique: 'Estudio de Localización Geográfica',
        label: 'Localización',
        icon: '📍',
    },
    [MGASection.VALUE_CHAIN]: {
        id: MGASection.VALUE_CHAIN,
        domain: 'Cadena de Valor',
        technique: 'Matriz de Cadena de Valor',
        label: 'Cadena de Valor',
        icon: '🔗',
    },
};

export const TABS = {
    DEVELOPMENT_PLAN: MGASection.DEVELOPMENT_PLAN,
    PROBLEM: MGASection.PROBLEM,
    PARTICIPANTS: MGASection.PARTICIPANTS,
    POPULATION: MGASection.POPULATION,
    OBJECTIVES: MGASection.OBJECTIVES,
    ALTERNATIVES: MGASection.ALTERNATIVES,
    REQUIREMENTS: MGASection.REQUIREMENTS,
    TECHNICAL_ANALYSIS: MGASection.TECHNICAL_ANALYSIS,
    LOCALIZATION: MGASection.LOCALIZATION,
    VALUE_CHAIN: MGASection.VALUE_CHAIN,
} as const;

export const MGA_VALIDATION_SECTION_TO_TAB: Record<string, MGASection> = {
    development_plans: MGASection.DEVELOPMENT_PLAN,
    problems: MGASection.PROBLEM,
    participants: MGASection.PARTICIPANTS,
    population: MGASection.POPULATION,
    objectives: MGASection.OBJECTIVES,
    alternatives: MGASection.ALTERNATIVES,
    requirements: MGASection.REQUIREMENTS,
    technical_analysis: MGASection.TECHNICAL_ANALYSIS,
    localization: MGASection.LOCALIZATION,
    value_chain: MGASection.VALUE_CHAIN,
};

export const PROJECT_STATUS = {
    DRAFT: 'draft',
    ACTIVE: 'active',
    COMPLETED: 'completed',
} as const;

export const POPULATION_TYPES = {
    AFFECTED: 'affected',
    INTERVENTION: 'intervention',
} as const;

export const MGA_STAGES = Object.values(MGA_SECTION_METADATA).map((meta) => ({
    id: meta.id,
    label: meta.label,
    domain: meta.domain,
    technique: meta.technique,
    icon: meta.icon,
}));

export const PAGINATION = {
    DEFAULT_PAGE_SIZE: 10,
    MAX_PAGE_SIZE: 100,
};
