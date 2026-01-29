/**
 * Error Boundary - Captura errores de React y muestra una UI alternativa
 */

import React, { ReactNode } from 'react';
import './ErrorBoundary.css';

interface Props {
    children: ReactNode;
}

interface State {
    hasError: boolean;
    error: Error | null;
    errorInfo: any;
}

class ErrorBoundary extends React.Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = { hasError: false, error: null, errorInfo: null };
    }

    static getDerivedStateFromError(error: Error) {
        return { hasError: true };
    }

    componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
        this.setState({
            error,
            errorInfo,
        });
        console.error('ErrorBoundary caught an error:', error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return (
                <div className="error-boundary-container">
                    <div className="error-boundary-content">
                        <h1>⚠️ Algo salió mal</h1>
                        <p>Disculpa, ha ocurrido un error inesperado.</p>

                        {process.env.NODE_ENV === 'development' && this.state.error && (
                            <details style={{ whiteSpace: 'pre-wrap', marginTop: '20px' }}>
                                <summary>Detalles del error (dev only)</summary>
                                <p>{this.state.error.toString()}</p>
                                {this.state.errorInfo && (
                                    <p>{this.state.errorInfo.componentStack}</p>
                                )}
                            </details>
                        )}

                        <button
                            onClick={() => {
                                this.setState({ hasError: false, error: null });
                                window.location.href = '/';
                            }}
                            className="error-boundary-button"
                        >
                            Volver al inicio
                        </button>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}

export default ErrorBoundary;
