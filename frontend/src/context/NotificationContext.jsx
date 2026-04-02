import React, { createContext, useContext, useState, useCallback, useRef } from "react";
import SuccessMessage from "../components/SuccessMessage";
import ConfirmationPopup from "../components/ConfirmationPopup";

const NotificationContext = createContext(null);

export function useNotification() {
    const ctx = useContext(NotificationContext);
    if (!ctx) throw new Error("useNotification must be used inside NotificationProvider");
    return ctx;
}

export function NotificationProvider({ children }) {
    // Success / Error toast
    const [toast, setToast] = useState({ visible: false, message: "", type: "success" });

    // Confirmation dialog
    const [confirmation, setConfirmation] = useState({ open: false, title: "", message: "", confirmText: "Eliminar", cancelText: "Cancelar" });
    const confirmResolveRef = useRef(null);

    const showSuccess = useCallback((message) => {
        setToast({ visible: true, message, type: "success" });
    }, []);

    const showError = useCallback((message) => {
        setToast({ visible: true, message, type: "error" });
    }, []);

    const hideToast = useCallback(() => {
        setToast(prev => ({ ...prev, visible: false }));
    }, []);

    const showConfirmation = useCallback(({ title, message, confirmText = "Eliminar", cancelText = "Cancelar" }) => {
        return new Promise((resolve) => {
            confirmResolveRef.current = resolve;
            setConfirmation({ open: true, title, message, confirmText, cancelText });
        });
    }, []);

    const handleConfirm = useCallback(() => {
        setConfirmation(prev => ({ ...prev, open: false }));
        confirmResolveRef.current?.(true);
        confirmResolveRef.current = null;
    }, []);

    const handleCancel = useCallback(() => {
        setConfirmation(prev => ({ ...prev, open: false }));
        confirmResolveRef.current?.(false);
        confirmResolveRef.current = null;
    }, []);

    return (
        <NotificationContext.Provider value={{ showSuccess, showError, showConfirmation }}>
            {children}

            <SuccessMessage
                message={toast.message}
                isVisible={toast.visible}
                onHide={hideToast}
                type={toast.type}
            />

            <ConfirmationPopup
                isOpen={confirmation.open}
                onConfirm={handleConfirm}
                onCancel={handleCancel}
                title={confirmation.title}
                message={confirmation.message}
                confirmText={confirmation.confirmText}
                cancelText={confirmation.cancelText}
            />
        </NotificationContext.Provider>
    );
}
