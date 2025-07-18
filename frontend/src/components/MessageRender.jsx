// MessageRenderer.jsx
import React from 'react';

const MessageRenderer = ({ text }) => {
    const formatText = (text) => {
        // Convertir saltos de línea a <br/>
        let formattedText = text.replace(/\n/g, "<br/>");

        // Convertir negritas (palabras entre **)
        formattedText = formattedText.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");

        // Puedes agregar más reglas para otros formatos, como listas, itálicas, etc.

        return formattedText;
    };

    return <div dangerouslySetInnerHTML={{ __html: formatText(text) }} />;
};

export default MessageRenderer;
