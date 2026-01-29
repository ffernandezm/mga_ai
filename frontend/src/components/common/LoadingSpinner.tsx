/**
 * Componente Loading Spinner
 * Muestra un indicador de carga
 */

import React from 'react';
import './LoadingSpinner.css';

interface LoadingSpinnerProps {
    message?: string;
    fullScreen?: boolean;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
    message = 'Cargando...',
    fullScreen = false,
}) => {
    return (
        <div className={`loading-spinner-container ${fullScreen ? 'fullscreen' : ''}`}>
            <div className="spinner">
                <div className="spinner-circle"></div>
            </div>
            {message && <p className="loading-message">{message}</p>}
        </div>
    );
};

export default LoadingSpinner;
