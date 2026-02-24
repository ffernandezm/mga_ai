/**
 * Tipos relacionados con Proyectos y MGA
 */

export interface Project {
    id: string | number;
    name: string;
    description: string;
    createdAt?: string;
    updatedAt?: string;
    status?: 'draft' | 'active' | 'completed';
}

export interface ProblemTree {
    id?: string | number;
    central_problem: string;
    current_description?: string;
    magnitude_problem?: string;
    direct_causes: Problem[];
    direct_effects: Problem[];
    indirect_causes?: Problem[];
    indirect_effects?: Problem[];
}

export interface Problem {
    id?: string | number;
    description: string;
    children?: Problem[];
    indirect_causes?: Problem[];
    indirect_effects?: Problem[];
    level?: number; // 1 = directo, 2 = indirecto
}

export interface Participant {
    id?: string | number;
    projectId: string | number;
    name: string;
    role: string;
    organization?: string;
    email?: string;
    phone?: string;
}

export interface Population {
    id?: string | number;
    projectId: string | number;
    type: 'affected' | 'intervention';
    name: string;
    description: string;
    size?: number;
    location?: string;
}

export interface Objective {
    id?: string | number;
    projectId: string | number;
    general_objective: string;
    general_problem: string;
    objectives_causes?: ObjectiveCause[];
    objectives_indicators?: ObjectiveIndicator[];
}

export interface ObjectiveCause {
    id?: string | number;
    objectiveId?: string | number;
    type: string;
    cause_related: string;
    specifics_objectives: string;
}

export interface ObjectiveIndicator {
    id?: string | number;
    objectiveId?: string | number;
    indicator: string;
    unit: string;
    meta: number;
    source_type: string;
    source_validation: string;
}

export interface Alternative {
    id?: string | number;
    projectId: string | number;
    name: string;
    description: string;
    advantages?: string[];
    disadvantages?: string[];
    costEstimate?: number;
}

export interface ProjectFormulation {
    projectId: string | number;
    problemTree?: ProblemTree;
    participants?: Participant[];
    populations?: Population[];
    objectives?: Objective[];
    alternatives?: Alternative[];
}
