import { createContext, useContext } from 'react';

// Crear contexto para la formulación
export const FormulationContext = createContext();

// Hook para usar el contexto
export const useFormulation = () => {
    const context = useContext(FormulationContext);
    if (!context) {
        console.warn('useFormulation debe usarse dentro de FormulationProvider');
        return {
            markModuleAsComplete: () => { },
            updateModuleCompletion: () => { },
            checkModuleCompletion: () => { }
        };
    }
    return context;
};

/**
 * Función helper para validar campos obligatorios
 * @param {Object} data - Datos a validar
 * @param {Array<string>} requiredFields - Array de nombres de campos obligatorios
 * @returns {boolean} true si todos los campos obligatorios tienen valor
 */
export const validateRequiredFields = (data, requiredFields) => {
    return requiredFields.every(field => {
        const value = data[field];
        // Verificar que el campo no sea null, undefined, vacío o array vacío
        if (Array.isArray(value)) {
            return value.length > 0;
        }
        return value !== null && value !== undefined && value !== '';
    });
};
