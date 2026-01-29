/**
 * Gestor de errores centralizado
 * Proporciona un mecanismo consistente para manejar errores en toda la aplicación
 */

import { ErrorResponse, ApiStatus } from '../types';

export class ApiError extends Error {
    public code: string;
    public statusCode?: number;
    public details?: Record<string, any>;

    constructor(
        message: string,
        code: string = 'UNKNOWN_ERROR',
        statusCode?: number,
        details?: Record<string, any>
    ) {
        super(message);
        this.name = 'ApiError';
        this.code = code;
        this.statusCode = statusCode;
        this.details = details;
    }

    toErrorResponse(): ErrorResponse {
        return {
            message: this.message,
            code: this.code,
            details: this.details,
        };
    }
}

export class NetworkError extends ApiError {
    constructor(message: string = 'Error de conexión de red') {
        super(message, 'NETWORK_ERROR');
        this.name = 'NetworkError';
    }
}

export class TimeoutError extends ApiError {
    constructor(message: string = 'La solicitud ha expirado') {
        super(message, 'TIMEOUT_ERROR');
        this.name = 'TimeoutError';
    }
}

export class ValidationError extends ApiError {
    constructor(message: string = 'Error de validación', details?: Record<string, any>) {
        super(message, 'VALIDATION_ERROR', 400, details);
        this.name = 'ValidationError';
    }
}

export const ErrorHandler = {
    /**
     * Convierte cualquier error en una instancia de ApiError normalizada
     */
    normalize(error: any): ApiError {
        if (error instanceof ApiError) {
            return error;
        }

        if (error?.response) {
            // Error de Axios
            const { status, data } = error.response;
            const message = data?.message || data?.error || error.message;
            return new ApiError(message, 'API_ERROR', status, data?.details);
        }

        if (error?.request) {
            // Error de red (no respuesta)
            return new NetworkError(error.message);
        }

        if (error instanceof Error) {
            return new ApiError(error.message, 'UNKNOWN_ERROR');
        }

        return new ApiError(String(error), 'UNKNOWN_ERROR');
    },

    /**
     * Obtiene un mensaje amigable para mostrar al usuario
     */
    getUserMessage(error: ApiError): string {
        const messages: Record<string, string> = {
            NETWORK_ERROR: 'No hay conexión. Por favor, verifica tu internet.',
            TIMEOUT_ERROR: 'La solicitud tardó demasiado. Intenta de nuevo.',
            VALIDATION_ERROR: 'Por favor, verifica los datos ingresados.',
            NOT_FOUND: 'Recurso no encontrado.',
            UNAUTHORIZED: 'No autorizado. Por favor, inicia sesión.',
            FORBIDDEN: 'No tienes permiso para realizar esta acción.',
            SERVER_ERROR: 'Error en el servidor. Intenta más tarde.',
            API_ERROR: 'Error al procesar la solicitud. Intenta de nuevo.',
        };

        return messages[error.code] || messages.API_ERROR || error.message;
    },

    /**
     * Log de errores (puede conectarse a Sentry, etc.)
     */
    log(error: ApiError, context?: string): void {
        const logData = {
            timestamp: new Date().toISOString(),
            name: error.name,
            code: error.code,
            message: error.message,
            statusCode: error.statusCode,
            details: error.details,
            context,
        };

        console.error('[API Error]', logData);

        // Aquí podrías enviar a un servicio de logging
        // if (process.env.NODE_ENV === 'production') {
        //   sendToErrorTracker(logData);
        // }
    },
};

export default ErrorHandler;
