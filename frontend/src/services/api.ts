/**
 * Servicio de API mejorado con:
 * - Tipado completo
 * - Interceptadores
 * - Manejo centralizado de errores
 * - Retry logic
 * - Configuración flexible
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosError } from 'axios';
import { ApiResponse, ApiConfig, ErrorResponse } from '../types';
import { ApiError, ErrorHandler } from './errorHandler';

class ApiService {
    private client: AxiosInstance;
    private config: ApiConfig;
    private retryCount = 0;
    private maxRetries = 3;

    constructor(config?: Partial<ApiConfig>) {
        this.config = {
            baseURL: config?.baseURL || process.env.REACT_APP_API_URL || 'http://localhost:8000',
            timeout: config?.timeout || 30000,
            headers: {
                'Content-Type': 'application/json',
                ...config?.headers,
            },
        };

        this.client = axios.create(this.config);
        this.setupInterceptors();
    }

    private setupInterceptors(): void {
        // Interceptor de request
        this.client.interceptors.request.use(
            (config) => {
                // Agregar token de autenticación si existe
                const token = localStorage.getItem('auth_token');
                if (token) {
                    config.headers.Authorization = `Bearer ${token}`;
                }
                return config;
            },
            (error) => {
                return Promise.reject(error);
            }
        );

        // Interceptor de response
        this.client.interceptors.response.use(
            (response) => response,
            async (error: AxiosError) => {
                const originalRequest = error.config as any;

                // Retry logic para errores de timeout
                if (
                    error.code === 'ECONNABORTED' &&
                    this.retryCount < this.maxRetries
                ) {
                    this.retryCount++;
                    await this.delay(1000 * this.retryCount);
                    return this.client(originalRequest);
                }

                this.retryCount = 0;

                // Manejar errores específicos
                if (error.response?.status === 401) {
                    // Redirigir a login
                    localStorage.removeItem('auth_token');
                    window.location.href = '/login';
                }

                return Promise.reject(error);
            }
        );
    }

    private delay(ms: number): Promise<void> {
        return new Promise((resolve) => setTimeout(resolve, ms));
    }

    /**
     * GET request
     */
    async get<T = any>(
        url: string,
        config?: AxiosRequestConfig
    ): Promise<T> {
        try {
            const response = await this.client.get<T>(url, config);
            return response.data;
        } catch (error) {
            const apiError = ErrorHandler.normalize(error);
            ErrorHandler.log(apiError, `GET ${url}`);
            throw apiError;
        }
    }

    /**
     * POST request
     */
    async post<T = any>(
        url: string,
        data?: any,
        config?: AxiosRequestConfig
    ): Promise<T> {
        try {
            const response = await this.client.post<T>(url, data, config);
            return response.data;
        } catch (error) {
            const apiError = ErrorHandler.normalize(error);
            ErrorHandler.log(apiError, `POST ${url}`);
            throw apiError;
        }
    }

    /**
     * PUT request
     */
    async put<T = any>(
        url: string,
        data?: any,
        config?: AxiosRequestConfig
    ): Promise<T> {
        try {
            const response = await this.client.put<T>(url, data, config);
            return response.data;
        } catch (error) {
            const apiError = ErrorHandler.normalize(error);
            ErrorHandler.log(apiError, `PUT ${url}`);
            throw apiError;
        }
    }

    /**
     * PATCH request
     */
    async patch<T = any>(
        url: string,
        data?: any,
        config?: AxiosRequestConfig
    ): Promise<T> {
        try {
            const response = await this.client.patch<T>(url, data, config);
            return response.data;
        } catch (error) {
            const apiError = ErrorHandler.normalize(error);
            ErrorHandler.log(apiError, `PATCH ${url}`);
            throw apiError;
        }
    }

    /**
     * DELETE request
     */
    async delete<T = any>(
        url: string,
        config?: AxiosRequestConfig
    ): Promise<T> {
        try {
            const response = await this.client.delete<T>(url, config);
            return response.data;
        } catch (error) {
            const apiError = ErrorHandler.normalize(error);
            ErrorHandler.log(apiError, `DELETE ${url}`);
            throw apiError;
        }
    }

    /**
     * Actualiza la configuración de la API
     */
    updateConfig(config: Partial<ApiConfig>): void {
        this.config = { ...this.config, ...config };
        if (config.baseURL) {
            this.client.defaults.baseURL = config.baseURL;
        }
    }

    /**
     * Obtiene la instancia del cliente Axios
     */
    getClient(): AxiosInstance {
        return this.client;
    }
}

// Crear y exportar instancia singleton
const apiService = new ApiService();
export default apiService;
