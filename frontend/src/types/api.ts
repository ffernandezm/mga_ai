/**
 * Tipos para respuestas de API
 */

export interface ApiErrorResponse {
    error: string;
    message: string;
    statusCode?: number;
    timestamp?: string;
}

export interface ChatHistoryItem {
    id?: string;
    message: string;
    sender: 'user' | 'bot';
    timestamp?: string;
}

export interface ChatResponse {
    message: string;
    success: boolean;
    conversationId?: string;
    tokens?: {
        input: number;
        output: number;
    };
}

export interface ApiConfig {
    baseURL: string;
    timeout?: number;
    headers?: Record<string, string>;
}
