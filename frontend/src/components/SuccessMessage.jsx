import React, { useEffect } from "react";
import "../styles/successMessage.css";

function SuccessMessage({ message, isVisible, onHide, type = "success" }) {
    useEffect(() => {
        if (isVisible) {
            const timer = setTimeout(() => {
                onHide();
            }, 3000);
            return () => clearTimeout(timer);
        }
    }, [isVisible, onHide]);

    if (!isVisible) return null;

    const isError = type === "error";

    return (
        <div className="success-message-overlay">
            <div className={`success-message ${isError ? "error-type" : ""}`}>
                <div className={`success-icon ${isError ? "error-icon-bg" : ""}`}>
                    {isError ? "✕" : "✓"}
                </div>
                <div className="success-content">
                    <h4>{isError ? "Error" : "¡Éxito!"}</h4>
                    <p>{message}</p>
                </div>
                <button className="success-close" onClick={onHide}>×</button>
            </div>
        </div>
    );
}

export default SuccessMessage;