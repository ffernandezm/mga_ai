/**
 * Hook para manejo de formularios
 * Simplifica la gestión de estado de formularios
 */

import { useState, useCallback } from 'react';

export interface UseFormOptions<T> {
    initialValues: T;
    onSubmit?: (values: T) => Promise<void> | void;
    validate?: (values: T) => Partial<T>;
}

export function useForm<T extends Record<string, any>>({
    initialValues,
    onSubmit,
    validate,
}: UseFormOptions<T>) {
    const [values, setValues] = useState<T>(initialValues);
    const [errors, setErrors] = useState<Partial<T>>({});
    const [touched, setTouched] = useState<Partial<Record<keyof T, boolean>>>({});
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleChange = useCallback(
        (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
            const { name, value, type } = e.target;
            const fieldValue = type === 'checkbox' ? (e.target as HTMLInputElement).checked : value;

            setValues((prev) => ({
                ...prev,
                [name]: fieldValue,
            }));

            // Validar en tiempo real si existe validación
            if (validate && touched[name as keyof T]) {
                const newErrors = validate({ ...values, [name]: fieldValue });
                setErrors((prev) => ({
                    ...prev,
                    [name]: newErrors[name as keyof T],
                }));
            }
        },
        [validate, touched, values]
    );

    const handleBlur = useCallback((e: React.FocusEvent<HTMLInputElement>) => {
        const { name } = e.target;
        setTouched((prev) => ({
            ...prev,
            [name]: true,
        }));

        // Validar cuando pierde el foco
        if (validate) {
            const newErrors = validate(values);
            setErrors((prev) => ({
                ...prev,
                [name]: newErrors[name as keyof T],
            }));
        }
    }, [validate, values]);

    const handleSubmit = useCallback(
        async (e: React.FormEvent<HTMLFormElement>) => {
            e.preventDefault();

            // Validar todos los campos
            if (validate) {
                const newErrors = validate(values);
                setErrors(newErrors);

                if (Object.keys(newErrors).length > 0) {
                    return;
                }
            }

            try {
                setIsSubmitting(true);
                if (onSubmit) {
                    await onSubmit(values);
                }
            } finally {
                setIsSubmitting(false);
            }
        },
        [values, validate, onSubmit]
    );

    const resetForm = useCallback(() => {
        setValues(initialValues);
        setErrors({});
        setTouched({});
    }, [initialValues]);

    const setFieldValue = useCallback((name: keyof T, value: any) => {
        setValues((prev) => ({
            ...prev,
            [name]: value,
        }));
    }, []);

    const setFieldError = useCallback((name: keyof T, error: string) => {
        setErrors((prev) => ({
            ...prev,
            [name]: error,
        }));
    }, []);

    return {
        values,
        errors,
        touched,
        isSubmitting,
        handleChange,
        handleBlur,
        handleSubmit,
        resetForm,
        setFieldValue,
        setFieldError,
    };
}
