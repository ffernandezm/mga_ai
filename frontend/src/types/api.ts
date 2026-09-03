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
    id?: string | number;
    message: string;
    sender: 'user' | 'bot';
    timestamp?: string;
    trace?: {
        active_section?: string;
        project_context_used?: boolean;
        rag_used?: boolean;
        sources?: Array<{
            document: string;
            page?: number | null;
            content: string;
            similarity: number;
        }>;
    } | null;
    suggested_changes?: Array<{
        field_key: string;
        field_label: string;
        field_type: string;
        current_value: string;
        suggested_value: string;
        confidence: string;
    }>;
    generation_status?: string | null;
    error?: string | null;
}

export interface ChatResponse {
    answer?: string | null;
    trace: {
        active_section?: string;
        project_context_used?: boolean;
        rag_used?: boolean;
        sources?: Array<{
            document: string;
            page?: number | null;
            content: string;
            similarity: number;
        }>;
    };
    suggested_changes: Array<{
        field_key: string;
        field_label: string;
        field_type: string;
        current_value: string;
        suggested_value: string;
        confidence: string;
    }>;
    generation_status: string;
    error?: string | null;
}

export interface ApiConfig {
    baseURL: string;
    timeout?: number;
    headers?: Record<string, string>;
}
