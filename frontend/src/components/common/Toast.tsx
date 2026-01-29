/**
 * Toast Notification Component
 * Muestra notificaciones no-intrusive al usuario
 */

import React, { useEffect } from 'react';
import './Toast.css';

interface ToastProps {
    id: string;
    message: string;
    type: 'success' | 'error' | 'warning' | 'info';
    duration?: number;
    onClose: (id: string) => void;
}

const Toast: React.FC<ToastProps> = ({
    id,
    message,
    type,
    duration = 4000,
    onClose,
}) => {
    useEffect(() => {
        const timer = setTimeout(() => {
            onClose(id);
        }, duration);

        return () => clearTimeout(timer);
    }, [id, duration, onClose]);

    const icons = {
        success: '✓',
        error: '✕',
        warning: '⚠',
        info: 'ℹ',
    };

    return (
        <div className={`toast toast-${type}`} role="alert">
            <span className="toast-icon">{icons[type]}</span>
            <span className="toast-message">{message}</span>
            <button
                className="toast-close"
                onClick={() => onClose(id)}
                aria-label="Cerrar notificación"
            >
                ×
            </button>
        </div>
    );
};

export default Toast;
