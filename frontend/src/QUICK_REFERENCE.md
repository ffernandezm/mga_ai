# 🎯 Validación de Campos Obligatorios - Guía Rápida

## ✅ Lo Nuevo

Sistema que **requiere validación de campos obligatorios** antes de desbloquear el siguiente módulo.

### Cambios Clave:

1. **Nuevo campo `is_completed`** en respuestas del API
   - `true` → módulo completado, desbloquea siguiente
   - `false` → módulo incomplete, bloquea siguiente
   - ausente → fallback a validación de datos

2. **Hook `useModuleValidation()`** - Simplifica implementación
3. **Función `validateRequiredFields()`** - Valida campos
4. **Función `validateArray()`** - Valida arrays de elementos

---

## 🚀 Implementación Rápida

### En tu Componente:

```jsx
import { useModuleValidation } from '../hooks/useModuleValidation';

function MiComponente({ projectId }) {
    const { saveAndValidate, validateArray } = useModuleValidation(
        'mi_modulo_id',           // ← Nombre del módulo
        '/mi-endpoint',            // ← Endpoint del API
        ['nombre', 'descripcion']  // ← Campos obligatorios
    );

    const handleSave = async () => {
        try {
            await saveAndValidate({
                nombre: formData.nombre,
                descripcion: formData.descripcion,
                // ✨ is_completed: true se añade automáticamente
            });
            toast.success('¡Guardado!');
        } catch (err) {
            toast.error(err.message);
        }
    };

    return (
        <button onClick={handleSave} disabled={!isValid()}>
            Guardar
        </button>
    );
}
```

---

## 📋 API Response Esperada

```json
{
    "id": 123,
    "projectId": 456,
    "nombre": "Mi Valor",
    "descripcion": "Descripción",
    "is_completed": true
}
```

**IMPORTANTE:** El backend DEBE retornar `is_completed: true`

---

## 🔒 Orden de Desbloqueo

```
Módulo 1 ✅ (siempre accesible)
  ↓ (si is_completed: true)
Módulo 2 (se desbloquea)
  ↓ (si is_completed: true)
Módulo 3 (se desbloquea)
  ... y así...
```

---

## 📚 Para Arrays (Participantes, Poblaciones, etc.)

```jsx
const { validateArray } = useModuleValidation(...);

// Validar que hay al menos 1 participante con nombre y rol
const isValid = validateArray(
    participantes,              // array
    1,                         // mínimo 1 item
    ['name', 'role']           // campos requeridos en cada item
);
```

---

## 📂 Archivos Modificados

- `src/types/project.ts` - Tipos con campo `is_completed`
- `src/pages/Formulation.jsx` - Lógica de validación mejorada
- `src/context/FormulationContext.jsx` - Helpers de validación
- `src/hooks/useModuleValidation.ts` - **NUEVO** Hook principal
- `src/VALIDATION_GUIDE.md` - Documentación completa
- `src/components/ExampleComponentWithValidation.jsx` - Ejemplo real

---

## ⚠️ Checklist de Implementación

Para cada componente de módulo:

- [ ] Importar `useModuleValidation` desde hooks
- [ ] Definir campos obligatorios del módulo
- [ ] Crear función de validación (o usar `validateArray`)
- [ ] Envolver guardado con `saveAndValidate()`
- [ ] Backend retorna `is_completed: true` cuando valida
- [ ] Probar que módulo siguiente se desbloquea

---

## 🐛 Troubleshooting

**Módulo no se desbloquea:**
- ✓ Revisar que backend retorna `is_completed: true`
- ✓ Revisar console por errores
- ✓ Verificar endpoint correcto
- ✓ Validar que `saveAndValidate()` fue llamado

**"Campos obligatorios faltantes":**
- ✓ Revisar campos en `validateRequiredFields()`
- ✓ Asegurar que todos los campos tengan valor
- ✓ No dejar campos vacíos (`''`) o null

**Array validation no funciona:**
- ✓ Usar `validateArray()` del hook
- ✓ Pasar array, cantidad mínima, campos requeridos
- ✓ Cada item debe tener los campos

---

## 📖 Referencias

- Documentación completa: `VALIDATION_GUIDE.md`
- Ejemplo completo: `ExampleComponentWithValidation.jsx`
- Contexto: `src/context/FormulationContext.jsx`
- Hook: `src/hooks/useModuleValidation.ts`
