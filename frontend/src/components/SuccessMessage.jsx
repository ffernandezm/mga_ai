import React, { useEffect } from "react";
import "../styles/successMessage.css";

function SuccessMessage({ message, isVisible, onHide }) {
    useEffect(() => {
        if (isVisible) {
            const timer = setTimeout(() => {
                onHide();
            }, 3000);
            return () => clearTimeout(timer);
        }
    }, [isVisible, onHide]);

    if (!isVisible) return null;

    return (
        <div className="success-message-overlay">
            <div className="success-message">
                <div className="success-icon">✓</div>
                <div className="success-content">
                    <h4>¡Éxito!</h4>
                    <p>{message}</p>
                </div>
                <button className="success-close" onClick={onHide}>×</button>
            </div>
        </div>
    );
}

export default SuccessMessage;