# Validación centralizada por sección MGA

## Fuente canónica

Las reglas determinísticas viven en `backend/app/section_validation/`. El LLM no decide completitud.

Estados:

- `NOT_STARTED`: no existe el registro raíz o ningún registro de la sección.
- `IN_PROGRESS`: existen datos, pero faltan campos o hay reglas bloqueantes.
- `COMPLETE`: las reglas representables por el modelo actual se cumplen.
- `BLOCKED`: falta al menos una dependencia indispensable.

`complete` expresa la completitud intrínseca de la sección. `prerequisites_complete` expresa si puede usarse como destino de navegación o contexto de generación.

## Matriz de reglas implementadas

| Sección | Modelo | Campo o relación real | Regla implementada | Etiqueta frontend/API |
|---|---|---|---|---|
| Plan de Desarrollo | `DevelopmentPlans` | `national_development_plan` | texto obligatorio | Articulación con el PND |
| Plan de Desarrollo | `DevelopmentPlans` | `program` | texto obligatorio | Programa relacionado |
| Plan de Desarrollo | `DevelopmentPlans` | planes territoriales + estrategia/programa correspondientes | estrategia y programa condicionales cuando se informa el plan | Estrategia/Programa del plan |
| Problemática | `Problems` | `central_problem` | texto obligatorio | Problema central |
| Problemática | `Problems` | `current_description` | texto obligatorio | Descripción de la situación existente |
| Problemática | `Problems` | `magnitude_problem` | texto obligatorio | Indicador o magnitud actual del problema |
| Problemática | `direct_causes`, `direct_effects` | `description` | al menos uno de cada tipo y ninguno vacío | Causa directa / Efecto directo |
| Participantes | `ParticipantsGeneral` | `participants_analisis` | texto obligatorio | Análisis general de participantes |
| Participantes | `Participants` | actor o entidad, `rol`, `interest_expectative` | al menos un participante y campos obligatorios | Actor, rol, intereses y expectativas |
| Participantes | `Participants` | `contribution_conflicts` | condicional para beneficiario, cooperante, oponente o perjudicado | Contribución / Estrategia de gestión |
| Población | `Population` | cantidades e información afectada/intervención | obligatorios; cantidades no negativas; objetivo no mayor a afectada | Cantidad/Fuente e información |
| Objetivos | `Objectives` | `general_objective` | texto obligatorio | Objetivo general |
| Objetivos | `ObjectivesCauses` | `specifics_objectives`, `cause_id` | al menos uno y cobertura de todas las causas directas | Objetivo específico |
| Objetivos | `ObjectivesIndicator` | `indicator`, `meta` | al menos un indicador con meta | Indicador de resultado / Meta |
| Alternativas | `Alternatives` | `name`, `active` | al menos una con nombre y exactamente una activa | Alternativa / Alternativa activa |
| Necesidades | `RequirementsGeneral` | `requirements_analysis` | texto obligatorio | Análisis de necesidades |
| Necesidades | `Requirement` | bien, unidad, oferta, demanda y años | obligatorios; horizonte cronológicamente consistente | Bien o servicio / Unidad / Oferta / Demanda / Horizonte |
| Análisis Técnico | `TechnicalAnalysis` | `analysis` | texto obligatorio | Descripción y requisitos del análisis técnico |
| Localización | `LocalizationGeneral.localizations` | región, departamento, ciudad, georreferenciación | al menos una; coordenadas cuando `georeferencing=true` | Localización / Coordenadas |
| Cadena de Valor | `ValueChainObjectives -> Product -> Activity` | FKs y descripciones | cadena y objetivos; productos no huérfanos; nombre; mínimo dos actividades; actividades no huérfanas ni vacías | Objetivo / Producto / Actividad |

## Gaps del modelo MGA 2023

Estos requisitos no se declaran implementados porque el esquema actual no los representa inequívocamente:

1. Problemática no separa línea base, unidad y fuente; `magnitude_problem` es texto único.
2. Participantes usa un solo campo `contribution_conflicts` para contribución y estrategia de gestión.
3. Población combina fuente, criterio y descripción en `population_info_*`; no existe justificación para objetivo mayor que afectada.
4. La asociación del objetivo general al problema es texto sincronizado, no una FK semántica.
5. Alternativas no tiene relación estructurada con acciones/objetivos. `active` se usa como selección operativa, pero `state` no tiene semántica canónica ni restricción única en base de datos.
6. Necesidades no relaciona requerimientos con alternativa/producto y no tiene series anuales numéricas de oferta/demanda. No puede calcularse `deficit = demanda - oferta` de forma determinística.
7. Análisis Técnico solo tiene `analysis`; no separa alternativa, productos, normativa, “No aplica” ni estudios adicionales.
8. Localización no tiene campo de justificación ni clasificación de infraestructura; macro/microlocalización no puede condicionarse con rigor.
9. Cadena de Valor no tiene modelo de insumos/rubros. `ValueChainObjectives` no tiene FK directa a `Objectives`; la asociación disponible pasa por `ObjectivesCauses`.
10. `PndDetail.selected_to_project` y el catálogo PND son globales, sin `project_id`; no sirven como selección PND aislada por proyecto.
11. Las marcas visuales `*`/`aria-required` quedaron alineadas en Problemática y ya existían parcialmente en Población/Participantes. Los demás formularios requieren una segunda pasada de UI para cubrir cada control dinámico sin inventar asociaciones DOM.
12. Los componentes no ofrecen un contrato común para “guardar cambios pendientes”. La navegación valida datos ya persistidos; no se declara implementado un guardado automático transversal.

No se agregó migración: cerrar los gaps 5 a 10 exige decisiones de producto y cambios de esquema que exceden una migración mínima segura.

## Endpoints

- `GET /projects/{project_id}/sections/{section}/validation`
- `GET /projects/{project_id}/sections/validation`

El endpoint de chat existente ahora responde `409` antes de persistir la pregunta cuando falta una dependencia indispensable. No exige que la sección activa esté completa.

## Ejemplos reales del contrato

Proyecto vacío, consultado mediante `SectionValidationService`:

### Problemática

```json
{
  "section": "problems",
  "status": "BLOCKED",
  "complete": false,
  "missing_fields": [
    {"key": "central_problem", "label": "Problema central", "path": "problems.central_problem", "message": "Este campo es obligatorio."},
    {"key": "current_description", "label": "Descripción de la situación existente", "path": "problems.current_description", "message": "Este campo es obligatorio."},
    {"key": "magnitude_problem", "label": "Indicador o magnitud actual del problema", "path": "problems.magnitude_problem", "message": "Este campo es obligatorio."},
    {"key": "direct_causes", "label": "Al menos una causa directa", "path": "direct_causes", "message": "Este campo es obligatorio."},
    {"key": "direct_effects", "label": "Al menos un efecto directo", "path": "direct_effects", "message": "Este campo es obligatorio."}
  ],
  "blocking_rules": [],
  "prerequisites_complete": false,
  "incomplete_prerequisites": ["development_plans"]
}
```

### Población

```json
{
  "section": "population",
  "status": "BLOCKED",
  "complete": false,
  "missing_fields": [
    {"key": "population_number_affected", "label": "Cantidad de población afectada", "path": "population.population_number_affected", "message": "Este campo es obligatorio."},
    {"key": "population_info_affected", "label": "Fuente e información de población afectada", "path": "population.population_info_affected", "message": "Este campo es obligatorio."},
    {"key": "population_number_intervention", "label": "Cantidad de población objetivo", "path": "population.population_number_intervention", "message": "Este campo es obligatorio."},
    {"key": "population_info_intervention", "label": "Fuente y criterio de población objetivo", "path": "population.population_info_intervention", "message": "Este campo es obligatorio."}
  ],
  "blocking_rules": [],
  "prerequisites_complete": false,
  "incomplete_prerequisites": ["problems"]
}
```

### Objetivos

```json
{
  "section": "objectives",
  "status": "BLOCKED",
  "complete": false,
  "missing_fields": [
    {"key": "general_objective", "label": "Objetivo general", "path": "objectives.general_objective", "message": "Este campo es obligatorio."},
    {"key": "specific_objectives", "label": "Al menos un objetivo específico", "path": "objectives_causes.specifics_objectives", "message": "Este campo es obligatorio."},
    {"key": "objectives_indicators", "label": "Indicador de resultado y meta", "path": "objectives_indicators", "message": "Este campo es obligatorio."}
  ],
  "blocking_rules": [],
  "prerequisites_complete": false,
  "incomplete_prerequisites": ["problems"]
}
```

### Cadena de Valor

```json
{
  "section": "value_chain",
  "status": "BLOCKED",
  "complete": false,
  "missing_fields": [
    {"key": "value_chains", "label": "Cadena de valor", "path": "value_chains", "message": "Este campo es obligatorio."},
    {"key": "value_chain_objectives", "label": "Objetivo específico de la cadena de valor", "path": "value_chain_objectives", "message": "Este campo es obligatorio."},
    {"key": "products", "label": "Al menos un producto", "path": "products", "message": "Este campo es obligatorio."}
  ],
  "blocking_rules": [],
  "prerequisites_complete": false,
  "incomplete_prerequisites": ["objectives", "alternatives", "requirements"]
}
```

## Pruebas ejecutadas

```text
frontend: npm run build -> correcto
backend: 124 passed
```

Suite backend ejecutada: validación de secciones, integración de chat, gestor/loaders de contexto y prompts LLM.
