"""
Sistema de Prompt Templates para MGA.

Genera prompts contextualizados y especializados para cada componente del árbol de problemas.
Cada template incluye contexto del documento, historial de chat, y datos del proyecto.

Componentes MGA soportados:
- problems: Árbol de problemas y análisis de causas/efectos
- participants: Identificación y análisis de actores clave
- population: Caracterización demográfica y de beneficiarios
- requirements_general: Identificación de requerimientos del proyecto
- objectives: Formulación de objetivos SMART e indicadores
- value_chain: Estructuración de la cadena de valor
- alternatives: Análisis de alternativas de solución
"""

import logging
import re
from typing import Dict

from langchain_core.prompts import PromptTemplate

# Configurar logging
logger = logging.getLogger(__name__)


class MgaPromptTemplate:
    """
    Gestor de prompts especializados para la Metodología General Ajustada (MGA).

    Proporciona templates personalizados para cada componente del proyecto,
    inyectando contexto de RAG, historial de chat y datos de otros componentes.
    """

    COMPONENT_PROMPTS: Dict[str, Dict[str, str]] = {
        "problems": {
            "name": "Árbol de Problemas",
            "template": """Eres un experto en formulación de proyectos usando la Metodología General Ajustada (MGA) de Colombia.

CONTEXTO DOCUMENTO CONCEPTUAL MGA:
{doc_context}

INFORMACIÓN DEL PROYECTO:
- Nombre del Proyecto: {project_name}
- Descripción: {project_description}

CHAT PREVIO (para mantener coherencia):
{chat_history}

ÁRBOL DE PROBLEMAS ACTUAL:
{current_problems}

Basándote en tus conocimientos de MGA y en el contexto del documento DOCUMENTO CONCEPTUAL MGA y la información del proyecto, por favor:

Céntrate en responder a la siguiente pregunta sin salirte del contexto sobre MGA:

Pregunta del usuario: {question}

Respuesta:""",
        },
        "participants": {
            "name": "Participantes y Actores",
            "template": """Eres un experto en análisis de actores y participantes en proyectos de inversión pública.

CONTEXTO DEL DOCUMENTO:
{doc_context}

INFORMACIÓN DEL PROYECTO:
- Nombre: {project_name}
- Población objetivo: {population_context}

ÁRBOL DE PROBLEMAS:
{problems_context}

CHAT PREVIO:
{chat_history}

PARTICIPANTES IDENTIFICADOS:
{current_participants}

Basándote en el contexto y el árbol de problemas, por favor:
1. Identifica actores clave (directos e indirectos)
2. Analiza sus intereses y motivaciones
3. Evalúa su poder e influencia
4. Sugiere mecanismos de participación

Pregunta del usuario: {question}

Respuesta:""",
        },
        "population": {
            "name": "Población y Beneficiarios",
            "template": """Eres un experto en caracterización de población y análisis de beneficiarios en proyectos MGA.

CONTEXTO DEL DOCUMENTO:
{doc_context}

INFORMACIÓN DEL PROYECTO:
- Proyecto: {project_name}
- Descripción: {project_description}

PARTICIPANTES CLAVE:
{participants_context}

CHAT PREVIO:
{chat_history}

POBLACIÓN ACTUAL:
{current_population}

Basándote en el contexto y los participantes identificados, por favor:
1. Caracteriza demográficamente a la población
2. Analiza condiciones socioeconómicas
3. Identifica grupos vulnerables o prioritarios
4. Propone criterios de selección de beneficiarios

Pregunta del usuario: {question}

Respuesta:""",
        },
        "requirements_general": {
            "name": "Requerimientos Generales",
            "template": """Eres un especialista en estructuración de requerimientos para proyectos de inversión pública bajo metodología MGA.

CONTEXTO DEL DOCUMENTO:
{doc_context}

INFORMACIÓN DEL PROYECTO:
- Proyecto: {project_name}
- Descripción: {project_description}

POBLACIÓN OBJETIVO:
{population_context}

OBJETIVOS DEFINIDOS:
{objectives_context}

CHAT PREVIO:
{chat_history}

REQUERIMIENTOS ACTUALES:
{current_requirements_general}

Con base en el contexto, por favor:
1. Identifica bienes y servicios requeridos
2. Propón criterios de calidad y cantidades de referencia
3. Señala brechas entre oferta y demanda cuando apliquen
4. Sugiere una priorización técnica inicial de requerimientos

Pregunta del usuario: {question}

Respuesta:""",
        },
        "objectives": {
            "name": "Objetivos del Proyecto",
            "template": """Eres un experto en formulación de objetivos SMART para proyectos de inversión pública.

CONTEXTO DEL DOCUMENTO:
{doc_context}

ÁRBOL DE PROBLEMAS:
{problems_context}

POBLACIÓN BENEFICIARIA:
{population_context}

CHAT PREVIO:
{chat_history}

OBJETIVOS ACTUALES:
{current_objectives}

Basándote en el árbol de problemas y la población, por favor:
1. Formula objetivo general claro y medible
2. Plantea objetivos específicos SMART
3. Establece indicadores de éxito
4. Define metas esperadas

Pregunta del usuario: {question}

Respuesta:""",
        },
        "value_chain": {
            "name": "Cadena de Valor",
            "template": """Eres un experto en diseño de cadena de valor para proyectos MGA en Colombia.

CONTEXTO DEL DOCUMENTO:
{doc_context}

INFORMACIÓN DEL PROYECTO:
- Proyecto: {project_name}
- Descripción: {project_description}

OBJETIVOS DEL PROYECTO:
{objectives_context}

REQUERIMIENTOS PRIORIZADOS:
{requirements_context}

CHAT PREVIO:
{chat_history}

CADENA DE VALOR ACTUAL:
{current_value_chain}

Con base en el contexto, por favor:
1. Define eslabones o etapas principales de la cadena de valor
2. Relaciona productos, actividades e insumos clave por etapa
3. Identifica cuellos de botella o riesgos operativos
4. Propón ajustes para mejorar eficiencia y trazabilidad

Pregunta del usuario: {question}

Respuesta:""",
        },
        "alternatives": {
            "name": "Alternativas de Solución",
            "template": """Eres un experto en análisis de alternativas y opciones de política pública.

CONTEXTO DEL DOCUMENTO:
{doc_context}

OBJETIVOS DEL PROYECTO:
{objectives_context}

PARTICIPANTES INVOLUCRADOS:
{participants_context}

CHAT PREVIO:
{chat_history}

ALTERNATIVAS PROPUESTAS:
{current_alternatives}

Basándote en los objetivos y participantes, por favor:
1. Plantea alternativas viables de solución
2. Analiza ventajas y desventajas de cada una
3. Estima costos y beneficios preliminares
4. Recomienda la alternativa más apropiada

Pregunta del usuario: {question}

Respuesta:""",
        },
    }

    @classmethod
    def _extract_input_variables(cls, template_str: str) -> list[str]:
        """Extrae variables de un template en formato {variable}."""
        variables = sorted(set(re.findall(r"{([a-zA-Z_][a-zA-Z0-9_]*)}", template_str)))
        return variables or ["question"]

    @classmethod
    def get_template(cls, component: str) -> PromptTemplate:
        """
        Obtiene el template de prompt para un componente MGA.

        Args:
            component: Componente MGA:
                - 'problems': Árbol de problemas
                - 'participants': Participantes y actores
                - 'population': Población beneficiaria
                - 'requirements_general': Requerimientos del proyecto
                - 'objectives': Objetivos del proyecto
                - 'value_chain': Cadena de valor
                - 'alternatives': Alternativas de solución

        Returns:
            PromptTemplate: Template configurado y listo para usar

        Raises:
            ValueError: Si el componente no es válido
        """
        if component not in cls.COMPONENT_PROMPTS:
            logger.error(f"Componente inválido: {component}")
            raise ValueError(
                f"Componente no válido: {component}. "
                f"Usar: {list(cls.COMPONENT_PROMPTS.keys())}"
            )

        template_str = cls.COMPONENT_PROMPTS[component]["template"]
        logger.debug(f"Template obtenido para: {component}")

        return PromptTemplate(
            input_variables=cls._extract_input_variables(template_str),
            template=template_str,
        )

    @classmethod
    def create_prompt(
        cls,
        component: str,
        question: str,
        doc_context: str,
        project_name: str = "Proyecto",
        project_description: str = "",
        chat_history: str = "",
        development_plans_context: str = "",
        problems_context: str = "",
        participants_context: str = "",
        population_context: str = "",
        requirements_context: str = "",
        objectives_context: str = "",
        value_chain_context: str = "",
        current_problems: str = "",
        current_participants: str = "",
        current_population: str = "",
        current_requirements_general: str = "",
        current_objectives: str = "",
        current_value_chain: str = "",
        current_alternatives: str = "",
    ) -> str:
        """Crea un prompt completamente formado para un componente MGA."""
        if component not in cls.COMPONENT_PROMPTS:
            logger.warning(f"Componente desconocido: {component} - usando template genérico")
            template_str = """Eres un experto en Metodología General Ajustada (MGA) para formulación de proyectos en Colombia.

CONTEXTO DEL DOCUMENTO:
{doc_context}

INFORMACIÓN DEL PROYECTO:
{project_name}: {project_description}

CHAT PREVIO:
{chat_history}

Basándote en el contexto y siendo coherente con la metodología MGA:

Pregunta del usuario: {question}

Respuesta:"""
        else:
            template_str = cls.COMPONENT_PROMPTS[component]["template"]
            logger.debug(f"Prompt creado para componente: {component}")

        try:
            prompt = template_str.format(
                doc_context=doc_context or "Contexto del documento MGA disponible",
                project_name=project_name,
                project_description=project_description or "",
                chat_history=chat_history or "[Sin chat previo]",
                question=question,
                development_plans_context=development_plans_context or "",
                problems_context=problems_context or "",
                participants_context=participants_context or "",
                population_context=population_context or "",
                requirements_context=requirements_context or "",
                objectives_context=objectives_context or "",
                value_chain_context=value_chain_context or "",
                current_problems=current_problems or "",
                current_participants=current_participants or "",
                current_population=current_population or "",
                current_requirements_general=current_requirements_general or "",
                current_objectives=current_objectives or "",
                current_value_chain=current_value_chain or "",
                current_alternatives=current_alternatives or "",
            )

            logger.info(f"Prompt generado: {len(prompt)} caracteres")
            return prompt

        except KeyError as e:
            logger.error(f"Error: Variable no encontrada en template: {e}")
            return f"Pregunta del usuario: {question}"
        except Exception as e:
            logger.error(f"Error creando prompt: {e}", exc_info=True)
            return f"Pregunta del usuario: {question}"
