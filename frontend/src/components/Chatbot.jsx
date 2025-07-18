import { useState } from "react";
import api from "../services/api";
import "../styles/Chatbot.css";
import MessageRenderer from "./MessageRender"; // Componente para renderizar mensajes

const Chatbot = ({ projectId }) => {
    const [messages, setMessages] = useState([
        { text: "¡Hola! ¿En qué puedo ayudarte?", sender: "bot" },
    ]);
    const [input, setInput] = useState("");

    const handleSend = async () => {
        if (input.trim() === "") return;

        setMessages((prev) => [...prev, { text: input, sender: "user" }]);
        setInput("");

        try {
            const response = await api.post(
                `/problems/response_ai/${projectId}?message=${encodeURIComponent(input)}`,
                {}
            );

            const botResponse = response.data.response || "No se obtuvo respuesta.";
            setMessages((prev) => [...prev, { text: botResponse, sender: "bot" }]);
        } catch (error) {
            console.error("Error consultando IA:", error);
            setMessages((prev) => [...prev, { text: "Error al obtener respuesta.", sender: "bot" }]);
        }
    };

    return (
        <div className="chat-container">
            <div className="chat-header">💬 Asistente Virtual</div>
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
