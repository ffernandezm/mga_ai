/**
 * Utilidades de validación
 * Proporciona funciones de validación reutilizables
 */

export const ValidationRules = {
    /**
     * Validar que un campo no esté vacío
     */
    required: (value: any): string | undefined => {
        if (!value || (typeof value === 'string' && value.trim() === '')) {
            return 'Este campo es obligatorio';
        }
        return undefined;
    },

    /**
     * Validar longitud mínima
     */
    minLength: (min: number) => (value: string): string | undefined => {
        if (value && value.length < min) {
            return `Mínimo ${min} caracteres`;
        }
        return undefined;
    },

    /**
     * Validar longitud máxima
     */
    maxLength: (max: number) => (value: string): string | undefined => {
        if (value && value.length > max) {
            return `Máximo ${max} caracteres`;
        }
        return undefined;
    },

    /**
     * Validar email
     */
    email: (value: string): string | undefined => {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (value && !emailRegex.test(value)) {
            return 'Email inválido';
        }
        return undefined;
    },

    /**
     * Validar número
     */
    number: (value: any): string | undefined => {
        if (value && isNaN(Number(value))) {
            return 'Debe ser un número';
        }
        return undefined;
    },

    /**
     * Validar rango numérico
     */
    range: (min: number, max: number) => (value: number): string | undefined => {
        if (value < min || value > max) {
            return `Debe estar entre ${min} y ${max}`;
        }
        return undefined;
    },

    /**
     * Validación personalizada
     */
    custom: (fn: (value: any) => boolean, message: string) => (value: any): string | undefined => {
        if (!fn(value)) {
            return message;
        }
        return undefined;
    },
};

/**
 * Combinador de validaciones
 */
export function compose(...rules: Array<(value: any) => string | undefined>) {
    return (value: any): string | undefined => {
        for (const rule of rules) {
            const error = rule(value);
            if (error) return error;
        }
        return undefined;
    };
}
