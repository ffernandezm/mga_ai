import { useState, useEffect } from "react";
import api from "../services/api";
import "../styles/Chatbot.css";
import MessageRenderer from "./MessageRender"; // Componente para renderizar mensajes

const Chatbot = ({ projectId, activeTab }) => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");

    // 🔹 Cargar historial al iniciar
    useEffect(() => {
        const fetchHistory = async () => {
            try {
                console.log("ingresando a chat inicial")
                console.log(projectId)
                console.log(activeTab)
                const response = await api.get(`chat_history/${projectId}/${activeTab}`);
                const history = response.data;
                console.log("historial de CHAT ")
                console.log(history)

                if (Array.isArray(history) && history.length > 0) {
                    // Transformar formato a [{ text, sender }]
                    const mapped = history.map(msg => ({
                        text: msg.message,
                        sender: msg.sender
                    }));
                    setMessages(mapped);
                } else {
                    setMessages([{ text: "¡Hola! ¿En qué puedo ayudarte?", sender: "bot" }]);
                }
            } catch (error) {
                console.warn("No hay historial, usando mensaje por defecto.");
                setMessages([{ text: "¡Hola! ¿En qué puedo ayudarte?", sender: "bot" }]);
            }
        };

        if (projectId && activeTab) {
            fetchHistory();
        }
    }, [projectId, activeTab]);

    const handleSend = async () => {
        if (input.trim() === "") return;

        // Agregar mensaje del usuario al estado
        setMessages((prev) => [...prev, { text: input, sender: "user" }]);
        const userMessage = input;
        setInput("");

        try {
            const response = await api.post(
                `/chat_history/chat/${projectId}/${activeTab}`,
                {
                    question: userMessage
                }
            );

            console.log("RESPUESTA DEL CHATBOT", response);

            const botResponse =
                response.data && response.data.message
                    ? response.data.message
                    : "No se obtuvo respuesta.";

            setMessages((prev) => [
                ...prev,
                { text: botResponse, sender: "bot" }
            ]);
        } catch (error) {
            console.error("Error consultando IA:", error);
            setMessages((prev) => [
                ...prev,
                { text: "Error al obtener respuesta.", sender: "bot" }
            ]);
        }
    };

    return (
        <div className="chat-container">
            <div className="chat-header">💬 Asistente Virtual </div>
            <div className="chat-box">
                {messages.map((msg, index) => (
                    <div key={index} className={`message ${msg.sender}`}>
                        <MessageRenderer text={msg.text} />
                    </div>
                ))}
            </div>
            <div className="input-box">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Escribe un mensaje..."
                    onKeyDown={(e) => e.key === "Enter" && handleSend()}
                />
                <button onClick={handleSend}>➤</button>
            </div>
        </div>
    );
};

export default Chatbot;
