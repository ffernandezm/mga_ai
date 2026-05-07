/**
 * EJEMPLO: Componente con Validación de Módulo
 * Este archivo muestra cómo implementar la validación de campos obligatorios
 * en un componente de formulation.
 * 
 * Este es un ejemplo educativo. Reemplaza [NOMBRE_COMPONENTE] con tu componente real.
 */

import { useState, useEffect } from 'react';
import { useModuleValidation } from '../hooks/useModuleValidation';
import { useNotification } from '../context/NotificationContext';
import api from '../services/api';

/**
 * Ejemplo: Componente de Participantes con Validación
 * 
 * Campos obligatorios:
 * - Al menos 1 participante
 * - Cada participante debe tener: name, role
 */
function ExampleComponentWithValidation({ projectId }) {
    // ========== Hooks ==========
    const { saveAndValidate, validateArray } = useModuleValidation(
        'participants_general',           // moduleId
        '/participants',                  // endpoint
        []                                // requiredFields (validamos items del array en su lugar)
    );
    const { toast } = useNotification();

    // ========== Estados ==========
    const [participants, setParticipants] = useState([]);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [formOpen, setFormOpen] = useState(false);
    const [newParticipant, setNewParticipant] = useState({
        name: '',
        role: ''
    });

    // ========== Efectos ==========
    useEffect(() => {
        const loadParticipants = async () => {
            try {
                const response = await api.get(`/participants/${projectId}`);
                setParticipants(response.data?.participants || []);
            } catch (err) {
                console.error('Error cargando participantes:', err);
                // No es error crítico si no hay datos
            } finally {
                setLoading(false);
            }
        };

        loadParticipants();
    }, [projectId]);

    // ========== Validaciones ==========
    const isNewParticipantValid = () => {
        return newParticipant.name.trim() !== '' && newParticipant.role.trim() !== '';
    };

    const canSave = () => {
        // Validar que hay al menos 1 participante y que cada uno tiene nombre y rol
        return validateArray(participants, 1, ['name', 'role']);
    };

    // ========== Manejadores ==========
    const handleAddParticipant = () => {
        if (!isNewParticipantValid()) {
            toast.error('Nombre y rol son obligatorios');
            return;
        }

        // Agregar participante
        setParticipants([...participants, { ...newParticipant }]);

        // Limpiar formulario
        setNewParticipant({ name: '', role: '' });
        setFormOpen(false);

        toast.success('Participante agregado');
    };

    const handleRemoveParticipant = (index) => {
        setParticipants(participants.filter((_, i) => i !== index));
        toast.info('Participante eliminado');
    };

    const handleSave = async () => {
        // Validar que hay datos para guardar
        if (!canSave()) {
            toast.error('Debe agregar al menos un participante con nombre y rol');
            return;
        }

        setSaving(true);
        try {
            // Usar saveAndValidate que se encarga de:
            // 1. Validar campos obligatorios
            // 2. Agregar is_completed: true
            // 3. Guardar en el backend
            // 4. Marcar el módulo como completado
            await saveAndValidate({
                participants,
                is_completed: true
            }, true); // skipValidation = true (ya validamos manualmente)

            toast.success('Participantes guardados exitosamente');
        } catch (err) {
            toast.error(err.message || 'Error guardando participantes');
            console.error('Error:', err);
        } finally {
            setSaving(false);
        }
    };

    // ========== Render ==========
    if (loading) {
        return <div className="text-center p-4">Cargando...</div>;
    }

    return (
        <div className="module-container">
            {/* Encabezado */}
            <div className="module-header mb-4">
                <h3>Participantes del Proyecto</h3>
                <p className="text-muted">
                    {participants.length > 0
                        ? `${participants.length} participante${participants.length !== 1 ? 's' : ''} agregado${participants.length !== 1 ? 's' : ''}`
                        : 'Agrega al menos un participante'}
                </p>
            </div>

            {/* Lista de Participantes */}
            {participants.length > 0 && (
                <div className="participants-list mb-4">
                    <table className="table table-sm">
                        <thead>
                            <tr>
                                <th>Nombre</th>
                                <th>Rol</th>
                                <th>Organización</th>
                                <th>Acciones</th>
                            </tr>
                        </thead>
                        <tbody>
                            {participants.map((p, index) => (
                                <tr key={index}>
                                    <td>{p.name}</td>
                                    <td>{p.role}</td>
                                    <td>{p.organization || '-'}</td>
                                    <td>
                                        <button
                                            className="btn btn-sm btn-danger"
                                            onClick={() => handleRemoveParticipant(index)}
                                        >
                                            Eliminar
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            {/* Formulario para Agregar */}
            {formOpen ? (
                <div className="form-section mb-4 p-3 border rounded">
                    <div className="form-group mb-2">
                        <label>Nombre *</label>
                        <input
                            type="text"
                            className="form-control"
                            value={newParticipant.name}
                            onChange={(e) =>
                                setNewParticipant({ ...newParticipant, name: e.target.value })
                            }
                            placeholder="Nombre del participante"
                        />
                    </div>

                    <div className="form-group mb-2">
                        <label>Rol *</label>
                        <input
                            type="text"
                            className="form-control"
                            value={newParticipant.role}
                            onChange={(e) =>
                                setNewParticipant({ ...newParticipant, role: e.target.value })
                            }
                            placeholder="Rol en el proyecto"
                        />
                    </div>

                    <div className="form-group mb-3">
                        <label>Organización</label>
                        <input
                            type="text"
                            className="form-control"
                            value={newParticipant.organization || ''}
                            onChange={(e) =>
                                setNewParticipant({ ...newParticipant, organization: e.target.value })
                            }
                            placeholder="Organización (opcional)"
                        />
                    </div>

                    <div className="d-flex gap-2">
                        <button
                            className="btn btn-sm btn-primary"
                            onClick={handleAddParticipant}
                        >
                            Agregar Participante
                        </button>
                        <button
                            className="btn btn-sm btn-secondary"
                            onClick={() => setFormOpen(false)}
                        >
                            Cancelar
                        </button>
                    </div>
                </div>
            ) : (
                <button
                    className="btn btn-outline-primary mb-4"
                    onClick={() => setFormOpen(true)}
                >
                    + Agregar Participante
                </button>
            )}

            {/* Botones de Acción */}
            <div className="action-buttons d-flex gap-2">
                <button
                    className="btn btn-success"
                    onClick={handleSave}
                    disabled={!canSave() || saving}
                >
                    {saving ? 'Guardando...' : '💾 Guardar Participantes'}
                </button>
                <small className="text-muted align-self-center">
                    {!canSave() && '❌ Completa los datos para guardar'}
                    {canSave() && '✅ Listo para guardar'}
                </small>
            </div>
        </div>
    );
}

export default ExampleComponentWithValidation;

/**
 * RESUMEN DE LA IMPLEMENTACIÓN:
 * 
 * 1. Hook useModuleValidation proporciona:
 *    - validateArray(): valida que el array tenga items con campos requeridos
 *    - saveAndValidate(): valida y guarda automáticamente
 *    - projectId, moduleId: información contextual
 * 
 * 2. Validaciones:
 *    - Frontend: verificamos antes de guardar
 *    - Backend: debe retornar is_completed: true
 * 
 * 3. Flujo de Guardado:
 *    - Usuario agrega datos
 *    - Usuario hace click en "Guardar"
 *    - saveAndValidate() valida y envía al backend
 *    - Backend retorna is_completed: true
 *    - Sistema marca módulo como completo
 *    - Siguiente módulo se desbloquea
 * 
 * 4. Manejo de Errores:
 *    - toast.error() para errores del usuario
 *    - try/catch para errores del servidor
 *    - Mensajes claros sobre validación
 */
