/**
 * Servicio para gestionar Chat con LLM
 * Centraliza todas las operaciones de conversación y chat
 */

import apiService from './api';
import { ChatMessage, ChatResponse, ChatSession, LLMResponse, ChatHistoryItem } from '../types';

type AxiosLike<T> = T | { data: T };

const unwrap = <T>(response: AxiosLike<T>): T => {
    if (response && typeof response === 'object' && 'data' in response) {
        return response.data;
    }
    return response;
};

const normalizeChatResponse = (response: AxiosLike<ChatResponse>): ChatResponse => {
    const payload = unwrap(response);
    return {
        answer: payload?.answer ?? null,
        trace: payload?.trace ?? null,
        suggested_changes: payload?.suggested_changes ?? [],
        generation_status: payload?.generation_status === 'error' ? 'error' : 'generated',
        error: payload?.error ?? null,
        error_type: payload?.error_type ?? null,
    };
};

class ChatService {
    /**
     * Obtener historial de chat
     */
    async getChatHistory(
        projectId: string | number,
        tab: string
    ): Promise<ChatHistoryItem[]> {
        try {
            const response = await apiService.get<ChatHistoryItem[] | { data: ChatHistoryItem[] }>(
                `/chat_history/${projectId}/${tab}`
            );
            return unwrap(response) || [];
        } catch (error) {
            console.warn('No hay historial disponible');
            return [];
        }
    }

    /**
     * Enviar mensaje al chat y obtener respuesta del LLM
     */
    async sendMessage(
        projectId: string | number,
        tab: string,
        question: string,
        requestFields?: Record<string, any>
    ): Promise<ChatResponse> {
        const response = await apiService.post<ChatResponse | { data: ChatResponse }>(
            `/chat_history/chat/${projectId}/${tab}`,
            {
                question,
                ...requestFields,
            }
        );
        return normalizeChatResponse(response);
    }

    /**
     * Generar sugerencias de IA basadas en contexto
     * (útil para autocompletar, sugerencias, etc.)
     */
    async generateSuggestions(
        projectId: string | number,
        tab: string,
        prompt: string,
        context?: Record<string, any>
    ): Promise<string[]> {
        try {
            const response = await apiService.post<{ suggestions: string[] }>(
                `/llm/suggestions/${projectId}/${tab}`,
                {
                    prompt,
                    context,
                }
            );
            return response.suggestions || [];
        } catch (error) {
            console.error('Error generating suggestions:', error);
            return [];
        }
    }

    /**
     * Analizar contenido con IA
     * Útil para análisis de problemas, objetivos, etc.
     */
    async analyzeContent(
        projectId: string | number,
        tab: string,
        content: string,
        analysisType: 'problems' | 'objectives' | 'alternatives' | 'general'
    ): Promise<LLMResponse> {
        return apiService.post<LLMResponse>(
            `/llm/analyze/${projectId}/${tab}`,
            {
                content,
                analysisType,
            }
        );
    }

    /**
     * Validar contenido con IA
     * Chequea completitud, coherencia, etc.
     */
    async validateContent(
        projectId: string | number,
        tab: string,
        content: Record<string, any>,
        validationType: 'problems' | 'objectives' | 'project'
    ): Promise<{ valid: boolean; issues: string[] }> {
        return apiService.post<{ valid: boolean; issues: string[] }>(
            `/llm/validate/${projectId}/${tab}`,
            {
                content,
                validationType,
            }
        );
    }

    /**
     * Generar sugerencias automáticas para un campo específico
     */
    async generateFieldSuggestions(
        projectId: string | number,
        tab: string,
        fieldType: string,
        currentValue: string,
        context?: Record<string, any>
    ): Promise<string[]> {
        try {
            const response = await apiService.post<{ suggestions: string[] }>(
                `/llm/field-suggestions/${projectId}/${tab}`,
                {
                    fieldType,
                    currentValue,
                    context,
                }
            );
            return response.suggestions || [];
        } catch (error) {
            console.error('Error generating field suggestions:', error);
            return [];
        }
    }

    /**
     * Mejorar/expandir texto con IA
     */
    async improveText(
        projectId: string | number,
        tab: string,
        text: string,
        improvement: 'clarify' | 'expand' | 'summarize' | 'formal'
    ): Promise<string> {
        const response = await apiService.post<{ improved_text: string }>(
            `/llm/improve-text/${projectId}/${tab}`,
            {
                text,
                improvement,
            }
        );
        return response.improved_text || text;
    }

    /**
     * Limpiar historial de chat
     */
    async clearHistory(projectId: string | number, tab: string): Promise<void> {
        await apiService.delete(`/chat_history/${projectId}/${tab}`);
    }
}

export default new ChatService();
