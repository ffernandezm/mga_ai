import React from "react";
import "../styles/ConfirmationPopup.css";
function ConfirmationPopup({
    isOpen,
    onConfirm,
    onCancel,
    title = "Confirmar eliminación",
    message = "¿Está seguro de que desea eliminar este elemento?",
    confirmText = "Eliminar",
    cancelText = "Cancelar"
}) {
    if (!isOpen) return null;

    return (
        <div className="confirmation-popup-overlay">
            <div className="confirmation-popup">
                <div className="confirmation-popup-header">
                    <h3>{title}</h3>
                </div>
                <div className="confirmation-popup-body">
                    <p>{message}</p>
                </div>
                <div className="confirmation-popup-footer">
                    <button
                        className="confirmation-button cancel-button"
                        onClick={onCancel}
                    >
                        {cancelText}
                    </button>
                    <button
                        className="confirmation-button confirm-button"
                        onClick={onConfirm}
                    >
                        {confirmText}
                    </button>
                </div>
            </div>
        </div>
    );
}

export default ConfirmationPopup;