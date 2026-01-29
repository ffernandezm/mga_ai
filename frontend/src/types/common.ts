/**
 * Tipos comunes reutilizables
 */

export interface ApiResponse<T = any> {
    data: T;
    status: number;
    message?: string;
    error?: string;
}

export interface PaginatedResponse<T> {
    data: T[];
    total: number;
    page: number;
    pageSize: number;
}

export interface ErrorResponse {
    message: string;
    code?: string;
    details?: Record<string, any>;
}

export type ApiStatus = 'idle' | 'loading' | 'success' | 'error';

export interface UseApiState<T> {
    data: T | null;
    loading: boolean;
    error: ErrorResponse | null;
    status: ApiStatus;
}

export interface MessageType {
    id?: string;
    text: string;
    sender: 'user' | 'bot';
    timestamp?: Date;
}

export interface ToastMessage {
    id: string;
    message: string;
    type: 'success' | 'error' | 'warning' | 'info';
    duration?: number;
}
