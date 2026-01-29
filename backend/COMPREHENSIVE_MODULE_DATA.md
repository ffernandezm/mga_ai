# 🎯 Función Avanzada: Recuperación de Datos Comprensivos del Módulo

## Descripción General

Se ha implementado una función completa y dinámica que recupera **TODA la información** de cualquier módulo registrado en el proyecto, incluyendo:

- ✅ Datos de la tabla principal
- ✅ Datos de TODAS las tablas relacionadas (subtablas)
- ✅ Estructura jerárquica multinivel (hasta 5 niveles de profundidad)
- ✅ Formato JSON para ser usado como contexto en prompts
- ✅ Sin hardcodear campos específicos - completamente dinámico

---

## Estructura Jerárquica de Módulos

### 📊 Problems (Problemas)
```
problems (tabla principal)
├── direct_effects (Efectos Directos)
│   └── indirect_effects (Efectos Indirectos)
└── direct_causes (Causas Directas)
    └── indirect_causes (Causas Indirectas)
```

**Ejemplo JSON:**
```json
{
  "central_problem": "Problema genérico",
  "current_description": "Descripción...",
  "direct_effects": [
    {
      "description": "Efecto 1",
      "indirect_effects": [
        {
          "description": "Efecto Indirecto 1"
        }
      ]
    }
  ],
  "direct_causes": [
    {
      "description": "Causa 1",
      "indirect_causes": [...]
    }
  ]
}
```

---

### 👥 ParticipantsGeneral (Actores)
```
participants_general (tabla principal)
└── participants (Participantes)
    ├── participant_actor
    ├── participant_entity
    ├── interest_expectative
    ├── rol
    └── contribution_conflicts
```

---

### 👫 Population (Población)
```
population (tabla principal)
├── affected_population (Población Afectada)
│   ├── region
│   ├── department
│   ├── city
│   ├── population_center
│   └── location_entity
├── intervention_population (Población de Intervención)
│   └── [mismos campos que affected_population]
└── characteristics_population (Características)
    ├── classification
    ├── detail
    ├── people_number
    └── information
```

**Contiene 24 características predefinidas:**
- Etapa del ciclo de vida (Primera infancia, Infancia, Adolescencia, etc.)
- Grupos étnicos (Indígenas, Afrocolombianos, etc.)
- Género (Masculino, Femenino)
- Población Vulnerable (Desplazados, Personas con discapacidad, etc.)

---

### 🎯 Objectives (Objetivos)
```
objectives (tabla principal)
├── objectives_causes (Causas del Objetivo)
└── objectives_indicators (Indicadores del Objetivo)
```

---

### 💡 AlternativesGeneral (Alternativas)
```
alternatives_general (tabla principal)
└── alternatives (Alternativas Específicas)
```

---

## Funciones Principales

### 1. `get_comprehensive_module_data(db, project_id, tab) → dict`

Recupera TODA la información de un módulo con estructura jerárquica.

**Parámetros:**
- `db` (Session): Sesión de BD de SQLAlchemy
- `project_id` (int): ID del proyecto
- `tab` (str): Nombre del módulo (problems, population, participants_general, objectives, alternatives_general)

**Retorna:**
```python
{
    "module": "problems",           # Nombre del módulo
    "table": "problems",            # Nombre de la tabla
    "total_records": 1,             # Total de registros en BD
    "records": [                    # Array de registros
        {
            "field1": "value1",
            "field2": "value2",
            "relation1": [          # Subtablas como arrays
                {
                    "sub_field1": "value"
                }
            ]
        }
    ]
}
```

**Ejemplo de uso:**
```python
from app.models.chat_history import get_comprehensive_module_data
from app.core.database import SessionLocal

db = SessionLocal()
data = get_comprehensive_module_data(db, project_id=1, tab='problems')
print(data)
```

---

### 2. `format_module_data_for_prompt(data, max_items=50) → str`

Convierte los datos JSON a formato legible y optimizado para prompts.

**Características:**
- Limita cantidad de items (default 50) para no sobrecargar contexto
- Añade encabezados informativos
- Formatea como JSON con indentación
- Incluye resumen de registros encontrados

**Ejemplo:**
```
================================================================================
📊 INFORMACIÓN COMPLETA DEL MÓDULO: PROBLEMS
================================================================================
Total de registros en BD: 1
Registros incluidos en contexto: 1

ESTRUCTURA JSON:
================================================================================
{
  "module": "problems",
  "total_records": 1,
  "records": [...]
}
================================================================================
```

---

## Integración en Chat

### Endpoint: `POST /chat_with_ai`

El endpoint `/chat_with_ai` ahora:

1. **Recupera historial de chat** - Mensajes anteriores de la conversación
2. **Obtiene datos completos del módulo** - Usa `get_comprehensive_module_data()`
3. **Formatea para el prompt** - Usa `format_module_data_for_prompt()`
4. **Pasa al LLM** - El contexto incluye:
   - Datos completos del módulo (estructura jerárquica)
   - Historial de chat anterior
   - Pregunta del usuario

**Flujo de contexto al LLM:**
```
Prompt = Módulo Context + Chat History + User Question
```

---

## Características Especiales

### ✅ Campos Ignorados Automáticamente
- IDs internos: `id`, `*_id` (excepto `project_id`)
- Timestamps: `created_at`, `updated_at`, `deleted_at`
- Campos JSON de modelos: `problem_tree_json`, `population_json`, `participants_json`, `alternatives_json`

### ✅ Relaciones Cargadas Dinámicamente
- Usa `joinedload()` para cargar relaciones anidadas
- Evita lazy loading que causaría múltiples queries
- Soporta hasta 5 niveles de profundidad

### ✅ Manejo de Errores
- Fallback graceful si hay errores de importación
- Logging de problemas con relaciones
- Respuesta informativa si tabla no existe

### ✅ Soporte Universal
- Funciona con ANY tabla en la BD
- No requiere hardcodear campos
- Dinámicamente detecta relaciones

---

## Tests Incluidos

### `test_comprehensive_module_data.py`
Prueba completa de:
- Descubrimiento de todas las tablas
- Recuperación de campos de cada tabla
- Módulos específicos (problems, population, participants_general, objectives, alternatives_general)
- Estructura jerárquica anidada
- Chat endpoint simulation

**Ejecución:**
```bash
python test_comprehensive_module_data.py
```

### `test_participants_relationship.py`
Debug específico para:
- Carga de relaciones sin joinedload
- Carga de relaciones con joinedload
- Inspección de atributos de relación
- Queries directas de datos

**Ejecución:**
```bash
python test_participants_relationship.py
```

---

## Mejoras Futuras

1. **Caché de datos** - Guardar datos en caché para queries frecuentes
2. **Agregaciones** - Resúmenes estadísticos de datos (ej: "Total de características de población: 24")
3. **Filtrado avanzado** - Permitir filtrar por campos específicos
4. **Paginación** - Para módulos con muchos registros
5. **Exportación** - Exportar datos a CSV/Excel

---

## Resumen de Cambios

| Archivo | Cambio | Impacto |
|---------|--------|--------|
| `app/models/chat_history.py` | +250 líneas: `get_comprehensive_module_data()`, `format_module_data_for_prompt()` | Alto - Nueva funcionalidad principal |
| `app/models/chat_history.py` | Mejorado: endpoint `/chat_with_ai` | Alto - Mejor contexto para LLM |
| `test_comprehensive_module_data.py` | Nuevo archivo | Pruebas automatizadas |
| `test_participants_relationship.py` | Nuevo archivo | Debug de relaciones |

---

## Status: ✅ COMPLETO Y FUNCIONAL

- ✅ Función principal implementada
- ✅ Formateador para prompts implementado  
- ✅ Integración en endpoint realizada
- ✅ Tests completos creados y ejecutados
- ✅ Estructura jerárquica verificada
- ✅ Documentación escrita

**Próximo paso:** Usar esta función en prompts reales para mejorar las respuestas del LLM.
