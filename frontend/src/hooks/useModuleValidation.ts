import { useCallback } from 'react';
import { useFormulation, validateRequiredFields } from '../context/FormulationContext';
import api from '../services/api';

/**
 * Hook para validar y guardar módulos en la formulation
 * @param {string} moduleId - ID del módulo (ej: 'participants_general')
 * @param {string} endpoint - Endpoint del API (ej: '/participants')
 * @param {Array<string>} requiredFields - Campos que deben estar llenos
 * @returns {Object} Métodos y estado para manejo del módulo
 */
export const useModuleValidation = (moduleId, endpoint, requiredFields = []) => {
    const { markModuleAsComplete, updateModuleCompletion, projectId } = useFormulation();

    /**
     * Valida que los campos obligatorios estén completados
     * @param {Object} data - Datos a validar
     * @returns {Object} { isValid: boolean, errors: Array<string> }
     */
    const validateData = useCallback((data) => {
        const errors = [];

        // Validar campos obligatorios generales
        if (requiredFields.length > 0) {
            if (!validateRequiredFields(data, requiredFields)) {
                errors.push(`Campos obligatorios faltantes: ${requiredFields.join(', ')}`);
            }
        }

        return {
            isValid: errors.length === 0,
            errors
        };
    }, [requiredFields]);

    /**
     * Guarda los datos en el backend y marca el módulo como completado
     * @param {Object} data - Datos a guardar
     * @param {boolean} skipValidation - Si true, no valida campos
     * @returns {Promise<Object>} Respuesta del servidor
     */
    const saveAndValidate = useCallback(async (data, skipValidation = false) => {
        if (!skipValidation) {
            const validation = validateData(data);
            if (!validation.isValid) {
                throw new Error(validation.errors.join('\n'));
            }
        }

        try {
            // Agregar is_completed = true al payload
            const payloadWithValidation = {
                ...data,
                is_completed: true
            };

            // Guardar en backend
            const response = await api.post(`${endpoint}/${projectId}`, payloadWithValidation);

            // Marcar módulo como completado en el estado local
            await markModuleAsComplete(moduleId);

            return response.data;
        } catch (err) {
            // Si hay error, marcar como incompleto
            await updateModuleCompletion(moduleId, false);
            throw err;
        }
    }, [moduleId, endpoint, projectId, markModuleAsComplete, updateModuleCompletion, validateData]);

    /**
     * Valida que un array tenga al menos items con ciertos campos
     * Útil para validar arrays de elementos (participantes, poblaciones, etc.)
     * @param {Array} array - Array a validar
     * @param {number} minItems - Cantidad mínima de items
     * @param {Array<string>} itemRequiredFields - Campos obligatorios en cada item
     * @returns {boolean}
     */
    const validateArray = useCallback((array, minItems = 1, itemRequiredFields = []) => {
        if (!Array.isArray(array) || array.length < minItems) {
            return false;
        }

        if (itemRequiredFields.length > 0) {
            return array.every(item => validateRequiredFields(item, itemRequiredFields));
        }

        return true;
    }, []);

    return {
        validateData,
        saveAndValidate,
        validateArray,
        projectId,
        moduleId
    };
};

export default useModuleValidation;
