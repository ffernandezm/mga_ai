# Rúbrica de evaluación — asistente LLM-RAG de MGA_IA

Evaluación **manual**. No se usa un LLM como evaluador automático.

Cada respuesta se califica de **1 a 5** en siete criterios. La calificación se
registra en el CSV de scoring, nunca dentro del JSONL de ejecución.

## Criterios

| # | Criterio | 1 | 3 | 5 |
|---|---|---|---|---|
| C1 | **Pertinencia** respecto a la pregunta | Responde otra cosa o regenera toda la sección sin que se lo pidan | Responde parcialmente lo preguntado | Responde exactamente lo preguntado, con el alcance solicitado |
| C2 | **Coherencia** con los datos del proyecto | Contradice lo registrado | Usa algunos datos reales y otros genéricos | Razona sobre los datos concretos del proyecto |
| C3 | **Precisión metodológica MGA** | Error conceptual (p. ej. confunde causa con efecto, producto con actividad) | Correcto pero superficial | Aplica correctamente la regla MGA y la explicita |
| C4 | **Uso del contexto** entregado | Ignora el contexto del proyecto y el RAG | Aprovecha uno de los dos | Integra datos del proyecto y fundamento metodológico |
| C5 | **Ausencia de invención** *(crítico)* | Inventa datos, cifras, actores o territorios | Afirma sin marcar que es una propuesta | No inventa; marca propuestas y declara lo faltante |
| C6 | **Claridad** | Confusa o con relleno | Aceptable | Concisa, estructurada y accionable |
| C7 | **Utilidad de la recomendación** | No aporta acción | Recomendación genérica | Acción concreta y aplicable a este proyecto |

## Agregación

- `avg` = promedio simple de C1–C7 (sin ponderaciones en esta primera evaluación).
- **`C5 = 1` ⇒ `failed = true`**, sin importar el promedio: una alucinación es
  descalificante.
- `blocking_issues`: texto libre para hallazgos que no caben en la escala.

## Uso de `expected.must` / `expected.must_not`

Los criterios del caso son la referencia objetiva del evaluador:

- cada `must` no cumplido baja **C1/C3** según corresponda;
- cada `must_not` incurrido baja **C5** si implica inventar, o **C1** si implica
  exceder el alcance de la pregunta.

## Comparación de variantes

| Variante | project_context | rag_context |
|---|---|---|
| A | vacío | vacío |
| B | contexto semántico | vacío |
| C | contexto semántico | Manual MGA 2015 recuperado |

Todo lo demás es idéntico: mismo prompt general, mismo prompt de sección, misma
pregunta, mismo historial (vacío en los 9 casos iniciales), misma configuración
de generación y mismo modelo.

Métricas derivadas: `delta B−A` mide el aporte del contexto estructurado y
`delta C−B` el aporte del RAG.
