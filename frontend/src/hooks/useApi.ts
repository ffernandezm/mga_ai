/**
 * Hook personalizado para manejo de API calls
 * Proporciona un patrón consistente para cargar datos
 */

import { useState, useCallback, useEffect } from 'react';
import { UseApiState, ErrorResponse, ApiStatus } from '../types';
import { ErrorHandler, ApiError } from '../services/errorHandler';

export function useApi<T>(
    apiCall: () => Promise<T>,
    dependencies: any[] = []
): UseApiState<T> & {
    refetch: () => Promise<void>;
    setData: (data: T | null) => void;
} {
    const [data, setData] = useState<T | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<ErrorResponse | null>(null);
    const [status, setStatus] = useState<ApiStatus>('idle');

    const execute = useCallback(async () => {
        try {
            setStatus('loading');
            setLoading(true);
            setError(null);

            const result = await apiCall();
            setData(result);
            setStatus('success');
        } catch (err) {
            const apiError = ErrorHandler.normalize(err);
            ErrorHandler.log(apiError, 'useApi');
            setError(apiError.toErrorResponse());
            setStatus('error');
        } finally {
            setLoading(false);
        }
    }, [apiCall]);

    const refetch = useCallback(async () => {
        await execute();
    }, [execute]);

    useEffect(() => {
        execute();
    }, dependencies);

    return {
        data,
        loading,
        error,
        status,
        refetch,
        setData,
    };
}
