"""
Sistema de Prompt Templates para MGA.

Genera prompts contextualizados y especializados para cada componente del árbol de problemas.
Cada template incluye contexto del documento, historial de chat, y datos del proyecto.

Componentes MGA soportados:
- problems: Árbol de problemas y análisis de causas/efectos
- participants: Identificación y análisis de actores clave
- population: Caracterización demográfica y de beneficiarios
- objectives: Formulación de objetivos SMART e indicadores
- alternatives: Análisis de alternativas de solución
"""

import logging
from typing import Dict, Optional, Any

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

Centrate en responder a la siguiente sin salirte del contexto sobre MGA:

Pregunta del usuario: {question}

Respuesta:"""
        },
        
        "participants": {
            "name": "Participantes y Actores",
            "template": """Eres un experto en análisis de actores y participantes en proyectos de inversión pública.

CONTEXTO DEL DOCUMENTO:
{doc_context}

INFORMACIÓN DEL PROYECTO:
- Nombre: {project_name}
- Población objetivo: {population_description}

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

Respuesta:"""
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

Respuesta:"""
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

Respuesta:"""
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

Respuesta:"""
        }
    }
    @classmethod
    def get_template(cls, component: str) -> PromptTemplate:
        """
        Obtiene el template de prompt para un componente MGA.
        
        Args:
            component: Componente MGA:
                - 'problems': Árbol de problemas
                - 'participants': Participantes y actores
                - 'population': Población beneficiaria
                - 'objectives': Objetivos del proyecto
                - 'alternatives': Alternativas de solución
        
        Returns:
            PromptTemplate: Template configurado y listo para usar
            
        Raises:
            ValueError: Si el componente no es válido
            
        Example:
            >>> template = MgaPromptTemplate.get_template("problems")
            >>> print(template.template[:100])
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
            input_variables=[
                "doc_context",
                "project_name",
                "project_description",
                "chat_history",
                "question"
            ],
            template=template_str
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
        problems_context: str = "",
        participants_context: str = "",
        population_context: str = "",
        objectives_context: str = "",
        current_problems: str = "",
        current_participants: str = "",
        current_population: str = "",
        current_objectives: str = "",
        current_alternatives: str = ""
    ) -> str:
        """
        Crea un prompt completamente formado para un componente MGA.
        
        Inyecta todos los contextos (RAG, historial, datos de otros componentes)
        en el template especializad para el componente, generando un prompt listo
        para enviar al LLM.
        
        Args:
            component: Componente MGA (problems, participants, population, objectives, alternatives)
            question: Pregunta del usuario a responder
            doc_context: Contexto recuperado del documento por RAG
            project_name: Nombre del proyecto
            project_description: Descripción del proyecto
            chat_history: Historial anterior de chat para coherencia
            problems_context: Contexto sobre problemas identificados
            participants_context: Contexto sobre participantes
            population_context: Contexto sobre población beneficiaria
            objectives_context: Contexto sobre objetivos
            current_problems: Problemas actuales del proyecto
            current_participants: Participantes actuales
            current_population: Población actual
            current_objectives: Objetivos actuales
            current_alternatives: Alternativas propuestas
        
        Returns:
            str: Prompt completamente formado listo para el LLM
            
        Example:
            >>> prompt = MgaPromptTemplate.create_prompt(
            ...     component="problems",
            ...     question="¿Cuál es el problema central?",
            ...     doc_context="Contexto del documento...",
            ...     project_name="Proyecto de salud"
            ... )
            >>> len(prompt) > 100
            True
        """
        if component not in cls.COMPONENT_PROMPTS:
            logger.warning(f"Componente desconocido: {component} - usando template genérico")
            # Template genérico para componentes desconocidos
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
            # Reemplazar variables en el template
            prompt = template_str.format(
                doc_context=doc_context or "Contexto del documento MGA disponible",
                project_name=project_name,
                project_description=project_description or "",
                chat_history=chat_history or "[Sin chat previo]",
                question=question,
                problems_context=problems_context or "",
                participants_context=participants_context or "",
                population_context=population_context or "",
                objectives_context=objectives_context or "",
                current_problems=current_problems or "",
                current_participants=current_participants or "",
                current_population=current_population or "",
                current_objectives=current_objectives or "",
                current_alternatives=current_alternatives or ""
            )
            
            logger.info(f"✅ Prompt generado: {len(prompt)} caracteres")
            return prompt
            
        except KeyError as e:
            logger.error(f"Error: Variable no encontrada en template: {e}")
            # Retornar prompt básico en caso de error
            return f"Pregunta del usuario: {question}"
        except Exception as e:
            logger.error(f"Error creando prompt: {e}", exc_info=True)
            # Retornar prompt básico en caso de error
            return f"Pregunta del usuario: {question}"
