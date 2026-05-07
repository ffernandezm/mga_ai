# Sistema de Validación de Módulos en Formulation

## Descripción General

El sistema valida que cada módulo tenga los campos obligatorios completados antes de permitir acceso al siguiente. Esto se controla a través de un campo `is_completed` en cada respuesta del API.

## Campos Requeridos por Módulo

### 1. **Plan de Desarrollo** (development_plans)
- Campos obligatorios: `name`, `description`
- Endpoint: `POST /development-plans/:projectId`

### 2. **Árbol de Problemas** (problems)
- Campos obligatorios: `central_problem`, `direct_causes`, `direct_effects`
- Endpoint: `POST /problems/:projectId`

### 3. **Participantes** (participants_general)
- Campos obligatorios: Al menos 1 participante con `name` y `role`
- Endpoint: `POST /participants`

### 4. **Población** (population)
- Campos obligatorios: Al menos 1 población afectada Y 1 de intervención
- Endpoint: `POST /populations`

### 5. **Objetivos** (objectives)
- Campos obligatorios: `general_objective`, `general_problem`
- Endpoint: `POST /objectives`

### 6. **Alternativas** (alternatives_general)
- Campos obligatorios: Al menos 1 alternativa con `name` y `description`
- Endpoint: `POST /alternatives`

### 7. **Necesidades** (requirements_general)
- Campos obligatorios: Al menos 1 requerimiento con `description`
- Endpoint: `POST /requirements`

### 8. **Análisis Técnico** (technical_analysis)
- Campos obligatorios: `analysis`
- Endpoint: `POST /technical-analysis/:projectId`

### 9. **Localización** (localization_general)
- Campos obligatorios: `location`
- Endpoint: `POST /localization/:projectId`

### 10. **Cadeba de Valor** (value_chain)
- Campos obligatorios: `description`
- Endpoint: `POST /value-chain/:projectId`

## Cómo Implementar en un Componente

### 1. Importar el Hook

```jsx
import { useFormulation, validateRequiredFields } from '../context/FormulationContext';
```

### 2. Usar el Hook

```jsx
function MiComponente({ projectId }) {
    const { markModuleAsComplete, updateModuleCompletion } = useFormulation();
    const [formData, setFormData] = useState({...});
    
    // Definir campos obligatorios
    const requiredFields = ['name', 'description', 'email'];
```

### 3. Validar y Guardar

```jsx
    const handleSave = async () => {
        // Validar campos obligatorios
        if (!validateRequiredFields(formData, requiredFields)) {
            toast.error('Por favor completa todos los campos obligatorios');
            return;
        }
        
        try {
            // Guardar datos
            const response = await api.post(`/mi-endpoint/${projectId}`, formData);
            
            // Marcar módulo como completado
            await markModuleAsComplete('mi_modulo_id');
            
            toast.success('Guardado exitosamente');
        } catch (err) {
            toast.error(err.message);
        }
    };
```

### 4. Respuesta del Backend

El backend debe devolver `is_completed: true` cuando valide que los campos obligatorios están completos:

```json
{
    "id": 123,
    "projectId": 456,
    "name": "Mi Plan",
    "description": "Descripción",
    "is_completed": true
}
```

## Flujo de Desbloqueo

```
1. Usuario abre formulación
2. Sistema verifica datos en backend
3. Módulo 1 se marca como accesible (siempre)
4. Usuario completa campos obligatorios en Módulo 1
5. Usuario guarda datos
6. Sistema marca is_completed = true en backend
7. Sistema verifica completitud y desbloquea Módulo 2
8. Proceso se repite para cada módulo
```

## Estructura del Backend Response

```typescript
// Respuesta exitosa con validación completada
{
    "id": 1,
    "projectId": 123,
    // ... otros campos del módulo
    "is_completed": true  // ✅ Módulo desbloqueado
}

// Respuesta con datos pero sin validar
{
    "id": 1,
    "projectId": 123,
    // ... otros campos del módulo
    "is_completed": false  // 🔒 Módulo bloqueado
}

// Sin datos
404 o []  // 🔒 Módulo bloqueado
```

## Ejemplo Completo: Componente de Participantes

```jsx
import { useFormulation, validateRequiredFields } from '../context/FormulationContext';
import { useNotification } from '../context/NotificationContext';

function Participants({ projectId }) {
    const { markModuleAsComplete } = useFormulation();
    const { toast } = useNotification();
    const [participants, setParticipants] = useState([]);
    const [newParticipant, setNewParticipant] = useState({
        name: '',
        role: ''
    });

    const handleAddParticipant = () => {
        // Validar campos obligatorios
        if (!validateRequiredFields(newParticipant, ['name', 'role'])) {
            toast.error('Nombre y rol son obligatorios');
            return;
        }

        setParticipants([...participants, newParticipant]);
        setNewParticipant({ name: '', role: '' });
    };

    const handleSave = async () => {
        if (participants.length === 0) {
            toast.error('Debe haber al menos un participante');
            return;
        }

        try {
            await api.post(`/participants`, {
                projectId,
                participants,
                is_completed: true
            });

            await markModuleAsComplete('participants_general');
            toast.success('Participantes guardados');
        } catch (err) {
            toast.error(err.message);
        }
    };

    return (
        <div>
            {/* Formulario */}
            <button onClick={handleSave}>Guardar</button>
        </div>
    );
}
```

## Verificación Manual

El sistema verifica cada módulo cuando:

1. **La página carga**: `checkModuleCompletion(projectId)` en el useEffect
2. **Se guarda un módulo**: `markModuleAsComplete(module)` después de guardar
3. **El usuario cambia de pestaña**: Se valida que sea accesible

## Notas Importantes

- ⚠️ No usar solo `response.data.length > 0`, verificar explícitamente `is_completed`
- ⚠️ El backend DEBE retornar `is_completed: true` cuando valide campos obligatorios
- ⚠️ Los campos obligatorios deben validarse ANTES de guardar en el frontend
- ✅ Usar `validateRequiredFields()` del contexto para consistencia
- ✅ Siempre llamar a `markModuleAsComplete()` después de guardar exitosamente
