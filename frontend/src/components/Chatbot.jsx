import { useEffect, useRef, useState } from "react";
import api from "../services/api";
import chatService from "../services/chatService";
import "../styles/Chatbot.css";
import MessageRenderer from "./MessageRender"; // Componente para renderizar mensajes
import { useNotification } from "../context/NotificationContext";

const CHAT_ACTIONS = [
    { key: "ask", label: "Preguntar", question: "" },
    { key: "review", label: "Revisar", question: "Revisa la información de esta sección." },
    { key: "improve", label: "Mejorar", question: "Propón una mejora del contenido de esta sección." },
    { key: "inconsistencies", label: "Detectar inconsistencias", question: "Detecta inconsistencias en esta sección." },
    { key: "missing", label: "¿Qué me falta?", question: "¿Qué información falta en esta sección?" },
];

const buildLocalMessageId = (prefix) => `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;

const buildWelcomeMessage = () => ({ id: buildLocalMessageId("welcome"), text: "¡Hola! ¿En qué puedo ayudarte?", sender: "bot" });

const normalizeHistoryMessage = (message) => ({
    id: message.id || buildLocalMessageId(message.sender || "message"),
    text: message.message || "",
    sender: message.sender,
    trace: message.trace || null,
    suggestedChanges: message.suggested_changes || [],
    generationStatus: message.generation_status || null,
    error: message.error || null,
    loading: false,
});

const Chatbot = ({ projectId, activeTab, evaluationSessionId, onApplySuggestedChanges }) => {
    const { showError, showConfirmation } = useNotification();
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const [isThinking, setIsThinking] = useState(false);
    const [suggestionModal, setSuggestionModal] = useState(null);
    const localStateVersionRef = useRef(0);

    // 🔹 Cargar historial al iniciar
    useEffect(() => {
        let cancelled = false;

        const fetchHistory = async () => {
            const expectedVersion = localStateVersionRef.current;

            try {
                console.log("ingresando a chat inicial")
                console.log(projectId)
                console.log(activeTab)
                const history = await chatService.getChatHistory(projectId, activeTab);
                console.log("historial de CHAT ")
                console.log(history)

                if (cancelled || localStateVersionRef.current !== expectedVersion) {
                    return;
                }

                if (Array.isArray(history) && history.length > 0) {
                    const mapped = history.map(normalizeHistoryMessage);
                    setMessages(mapped);
                } else {
                    setMessages([buildWelcomeMessage()]);
                }
            } catch (error) {
                if (cancelled || localStateVersionRef.current !== expectedVersion) {
                    return;
                }
                console.warn("No hay historial, usando mensaje por defecto.");
                setMessages([buildWelcomeMessage()]);
            }
        };

        if (projectId && activeTab) {
            fetchHistory();
        }

        return () => {
            cancelled = true;
            localStateVersionRef.current += 1;
        };
    }, [projectId, activeTab]);

    const handleSend = async (selectedAction = "ask", suppliedQuestion) => {
        const question = suppliedQuestion || input;
        if (question.trim() === "" || isThinking) return;

        const userMessageId = buildLocalMessageId("user");
        const pendingId = buildLocalMessageId("pending");
        localStateVersionRef.current += 1;
        const requestVersion = localStateVersionRef.current;

        // Agregar mensaje del usuario al estado
        setMessages((prev) => [
            ...prev,
            { id: userMessageId, text: question, sender: "user" },
            { id: pendingId, text: "", sender: "bot", loading: true, trace: null, suggestedChanges: [], generationStatus: "pending", error: null },
        ]);
        const userMessage = question;
        setInput("");
        setIsThinking(true);

        try {
            const response = await chatService.sendMessage(projectId, activeTab, userMessage, {
                action: selectedAction,
                evaluation_session_id: evaluationSessionId || undefined,
            });
            console.log("RESPUESTA DEL CHATBOT", response);

            const hasGeneratedAnswer = response?.generation_status === "generated"
                && typeof response.answer === "string"
                && response.answer.trim() !== "";
            const botResponse = hasGeneratedAnswer
                ? response.answer
                : response?.generation_status === "error"
                    ? (response.error || "El asistente no pudo generar una respuesta.")
                    : "";

            if (localStateVersionRef.current !== requestVersion) return;
            setMessages((prev) => prev.map((msg) => (
                msg.id === pendingId
                    ? {
                        ...msg,
                        text: botResponse,
                        trace: response.trace,
                        suggestedChanges: response.suggested_changes ?? [],
                        generationStatus: response.generation_status,
                        error: response.error || null,
                        loading: false,
                    }
                    : msg
            )));
        } catch (error) {
            console.error("Error consultando IA:", error);
            if (localStateVersionRef.current !== requestVersion) return;
            setMessages((prev) => prev.map((msg) => (
                msg.id === pendingId
                    ? { ...msg, text: "Error al obtener respuesta.", generationStatus: "error", loading: false, error: "Error al obtener respuesta." }
                    : msg
            )));
        } finally {
            if (localStateVersionRef.current === requestVersion) {
                setIsThinking(false);
            }
        }
    };

    const recordSuggestionDecision = async (eventType) => {
        if (!evaluationSessionId) return;
        try {
            await api.post(`/evaluation/sessions/${evaluationSessionId}/events`, {
                section: activeTab,
                event_type: eventType,
                payload: { source: "chat" },
            });
        } catch (error) {
            console.warn("No se pudo registrar la decisión de sugerencia", error);
        }
    };

    const copySuggestion = async (text) => {
        await navigator.clipboard?.writeText(text);
    };

    const useSuggestion = async (text, changes = []) => {
        if (changes.length) {
            setSuggestionModal({ changes, selected: new Set(changes.map((change) => change.field_key)) });
            return;
        }
        const confirmed = await showConfirmation({
            title: "Confirmar sugerencia",
            message: "La propuesta se copiará para que usted decida dónde aplicarla. No se actualizará ningún dato automáticamente.",
            confirmText: "Confirmar",
        });
        if (!confirmed) return;
        await copySuggestion(text);
        await recordSuggestionDecision("suggestion_accepted");
    };

    const confirmSuggestedChanges = async () => {
        const selectedChanges = suggestionModal.changes.filter((change) => suggestionModal.selected.has(change.field_key));
        if (selectedChanges.length) {
            onApplySuggestedChanges?.(selectedChanges);
            await recordSuggestionDecision("suggestion_accepted");
        }
        setSuggestionModal(null);
    };

    const handleDeleteChat = async () => {
        const confirmed = await showConfirmation({
            title: "Limpiar chat",
            message: "¿Está seguro de que desea limpiar todo el historial del chat?",
            confirmText: "Limpiar"
        });
        if (!confirmed) return;
        try {
            await api.delete(`/chat_history/${projectId}/${activeTab}`);
            localStateVersionRef.current += 1;
            setMessages([buildWelcomeMessage()]);
        } catch (error) {
            console.error("Error al limpiar el chat:", error);
            showError("Error al limpiar el chat. Intenta de nuevo.");
        }
    };

    return (
        <div className="chatbot-panel">
            <div className="chat-header">
                <div className="chat-title">💬 Asistente Virtual</div>
                <button
                    className="clear-chat-btn"
                    onClick={handleDeleteChat}
                    title="Limpiar chat"
                >
                    🗑️
                </button>
            </div>
            <div className="chat-box">
                {messages.map((msg, index) => {
                    const hasSources = Array.isArray(msg.trace?.sources) && msg.trace.sources.length > 0;

                    return <div key={msg.id || `${msg.sender}-${index}`} className={`message ${msg.sender}`}>
                        {msg.loading ? (
                            <div className="thinking-message" aria-live="polite" aria-label="El asistente esta escribiendo">
                                <span className="thinking-dot" />
                                <span className="thinking-dot" />
                                <span className="thinking-dot" />
                            </div>
                        ) : (
                            <MessageRenderer text={msg.text} />
                        )}
                        {msg.sender === "bot" && index > 0 && !msg.loading && (
                            <div className="chat-suggestion-actions">
                                <button title="Copiar respuesta" onClick={() => copySuggestion(msg.text)}>Copiar</button>
                                <button title="Ver comparación" onClick={() => window.alert(`Propuesta del asistente:\n\n${msg.text}`)}>Comparar</button>
                                <button title="Usar propuesta estructurada o copiar manualmente" onClick={() => useSuggestion(msg.text, msg.suggestedChanges)}>Usar sugerencia</button>
                                <button title="Descartar sugerencia" onClick={() => recordSuggestionDecision("suggestion_rejected")}>Descartar</button>
                            </div>
                        )}
                        {hasSources && !msg.loading && (
                            <details className="chat-trace">
                                <summary>Ver fuentes</summary>
                                <p>Sección: {msg.trace.active_section}. Contexto del proyecto: {msg.trace.project_context_used ? "usado" : "no usado"}. RAG: {msg.trace.rag_used ? "usado" : "no usado"}.</p>
                                {msg.trace.sources.map((source, sourceIndex) => <article key={`${source.document || "source"}-${source.page || sourceIndex}-${sourceIndex}`}><strong>{source.document}</strong>{source.page ? `, página ${source.page}` : ""} (similitud {source.similarity})<p>{source.content}</p></article>)}
                            </details>
                        )}
                    </div>;
                })}
            </div>
            <div className="chat-actions" aria-label="Acciones del asistente">
                {CHAT_ACTIONS.map((action) => <button key={action.key} onClick={() => action.key === "ask" ? null : handleSend(action.key, action.question)} disabled={isThinking}>{action.label}</button>)}
            </div>
            <div className="input-box">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Escribe un mensaje..."
                    onKeyDown={(e) => e.key === "Enter" && handleSend()}
                    disabled={isThinking}
                />
                <button onClick={() => handleSend()} disabled={isThinking}>➤</button>
            </div>
            {suggestionModal && <div className="suggestion-modal-backdrop" role="presentation">
                <section className="suggestion-modal" role="dialog" aria-modal="true" aria-label="Usar sugerencias">
                    <h3>Usar sugerencias</h3>
                    {suggestionModal.changes.map((change) => <label key={change.field_key} className="suggestion-change">
                        <input type="checkbox" checked={suggestionModal.selected.has(change.field_key)} onChange={() => setSuggestionModal((current) => {
                            const selected = new Set(current.selected);
                            selected.has(change.field_key) ? selected.delete(change.field_key) : selected.add(change.field_key);
                            return { ...current, selected };
                        })} />
                        <strong>{change.field_label}</strong><span>Valor actual: {change.current_value}</span><span>Valor propuesto: {change.suggested_value}</span>
                    </label>)}
                    <div><button onClick={() => setSuggestionModal(null)}>Cancelar</button><button onClick={confirmSuggestedChanges}>Usar sugerencia</button></div>
                </section>
            </div>}
        </div>
    );
};

export default Chatbot;
