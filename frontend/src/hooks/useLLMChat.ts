/**
 * Hook personalizado para chat con LLM
 * Maneja todo el estado y lógica de conversación
 */

import { useState, useCallback, useEffect } from 'react';
import chatService from '../services/chatService';
import { ChatMessage, MessageType } from '../types';
import { ErrorHandler, ApiError } from '../services/errorHandler';

export function useLLMChat(projectId: string | number, tab?: string) {
    const [messages, setMessages] = useState<MessageType[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [input, setInput] = useState('');

    // Cargar historial al inicializar
    useEffect(() => {
        if (!projectId || !tab) return;

        const loadHistory = async () => {
            try {
                setLoading(true);
                const history = await chatService.getChatHistory(projectId, tab);

                if (Array.isArray(history) && history.length > 0) {
                    const mapped = history.map((msg) => ({
                        id: msg.id,
                        text: msg.message,
                        sender: msg.sender as 'user' | 'bot',
                        timestamp: msg.timestamp ? new Date(msg.timestamp) : undefined,
                    }));
                    setMessages(mapped);
                } else {
                    setMessages([
                        {
                            text: '¡Hola! ¿En qué puedo ayudarte?',
                            sender: 'bot',
                            timestamp: new Date(),
                        },
                    ]);
                }
            } catch (err) {
                console.warn('No hay historial disponible');
                setMessages([
                    {
                        text: '¡Hola! ¿En qué puedo ayudarte?',
                        sender: 'bot',
                        timestamp: new Date(),
                    },
                ]);
            } finally {
                setLoading(false);
            }
        };

        loadHistory();
    }, [projectId, tab]);

    // Enviar mensaje
    const sendMessage = useCallback(
        async (message: string) => {
            if (!message.trim() || !projectId || !tab) return;

            try {
                setError(null);
                setLoading(true);

                // Agregar mensaje del usuario
                setMessages((prev) => [
                    ...prev,
                    {
                        text: message,
                        sender: 'user',
                        timestamp: new Date(),
                    },
                ]);

                setInput('');

                // Obtener respuesta del bot
                const response = await chatService.sendMessage(projectId, tab, message);

                // Agregar respuesta del bot
                setMessages((prev) => [
                    ...prev,
                    {
                        text: response.message,
                        sender: 'bot',
                        timestamp: new Date(),
                    },
                ]);
            } catch (err) {
                const apiError = ErrorHandler.normalize(err);
                const errorMsg = ErrorHandler.getUserMessage(apiError);
                setError(errorMsg);
                ErrorHandler.log(apiError, 'useLLMChat.sendMessage');

                // Agregar mensaje de error
                setMessages((prev) => [
                    ...prev,
                    {
                        text: `Error: ${errorMsg}`,
                        sender: 'bot',
                        timestamp: new Date(),
                    },
                ]);
            } finally {
                setLoading(false);
            }
        },
        [projectId, tab]
    );

    // Limpiar historial
    const clearHistory = useCallback(async () => {
        if (!projectId || !tab) return;

        try {
            await chatService.clearHistory(projectId, tab);
            setMessages([
                {
                    text: '¡Hola! ¿En qué puedo ayudarte?',
                    sender: 'bot',
                    timestamp: new Date(),
                },
            ]);
        } catch (err) {
            const apiError = ErrorHandler.normalize(err);
            ErrorHandler.log(apiError, 'useLLMChat.clearHistory');
        }
    }, [projectId, tab]);

    return {
        messages,
        loading,
        error,
        input,
        setInput,
        sendMessage,
        clearHistory,
        setMessages,
    };
}
