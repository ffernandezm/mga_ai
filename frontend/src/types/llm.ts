/**
 * Tipos para integración con LLM
 */

export interface LLMRequest {
    question: string;
    context?: string;
    conversationId?: string;
    projectId?: string | number;
    tab?: string;
}

export interface LLMResponse {
    message: string;
    success: boolean;
    conversationId?: string;
    suggestions?: string[];
    confidence?: number;
}

export interface ChatSession {
    id: string;
    projectId: string | number;
    tab: string;
    messages: ChatMessage[];
    createdAt: Date;
    updatedAt: Date;
}

export interface ChatMessage {
    id?: string;
    role: 'user' | 'assistant';
    content: string;
    tokens?: {
        input: number;
        output: number;
    };
    timestamp?: Date;
}

export interface LLMConfig {
    model: string;
    temperature: number;
    maxTokens: number;
    topP?: number;
}

export interface LLMStreamEvent {
    type: 'start' | 'chunk' | 'end' | 'error';
    data?: {
        chunk?: string;
        tokens?: number;
        error?: string;
    };
}
