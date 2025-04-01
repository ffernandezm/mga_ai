import { useState } from "react";
import api from "../services/api";
import "../styles/Chatbot.css";
import MessageRenderer from "./MessageRender"; // Importar el componente MessageRenderer

const Chatbot = ({ projectId }) => {
    const [messages, setMessages] = useState([
        { text: "¡Hola! ¿En qué puedo ayudarte?", sender: "bot" },
    ]);
    const [input, setInput] = useState("");

    const handleSend = async () => {
        if (input.trim() === "") return;

        // Agregar el mensaje del usuario al historial
        setMessages((prev) => [...prev, { text: input, sender: "user" }]);
        setInput("");

        try {
            const jsonData = {}; // JSON vacío si no hay datos adicionales
            const response = await api.post(
                `/problems/response_ai/${projectId}?message=${encodeURIComponent(input)}`,
                jsonData
            );

            // Obtener la respuesta de la API
            const botResponse = response.data.response || "No se obtuvo respuesta.";

            // Agregar la respuesta del bot al historial
            setMessages((prev) => [...prev, { text: botResponse, sender: "bot" }]);
        } catch (error) {
            console.error("Error consultando IA:", error);
            setMessages((prev) => [...prev, { text: "Error al obtener respuesta.", sender: "bot" }]);
        }
    };

    return (
        <div className="chat-container">
            <div className="chat-box">
                {messages.map((msg, index) => (
                    <div key={index} className={`message ${msg.sender}`}>
                        {/* Renderizamos el mensaje usando MessageRenderer */}
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
                />
                <button onClick={handleSend}>Enviar</button>
            </div>
        </div>
    );
};

export default Chatbot;
