import React from "react";
import "../styles/AIResponse.css";
import ReactMarkdown from "react-markdown";

function AIResponse({ response }) {
    if (!response) return null;

    return (
        <div className="ai-response warning">
            <ReactMarkdown>{response.response}</ReactMarkdown>
        </div>
    );
}

export default AIResponse;