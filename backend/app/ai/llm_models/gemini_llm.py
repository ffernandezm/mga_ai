"""
Google Gemini LLM Integration for MGA (Legacy/Alternative Provider).

Proporciona un chatbot basado en Google Generative AI (Gemini)
como proveedor alternativo a Groq.

NOTA: El proveedor preferido es GROQ (configurado en .env).
Este módulo se mantiene como alternativa.
"""

import os
import logging
from typing import Optional
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Configurar logging
load_dotenv()
logger = logging.getLogger(__name__)


class ChatBotModel:
    """
    Chatbot para MGA usando Google Generative AI (Gemini).
    
    NOTA: Se recomienda usar Groq LLMManager como proveedor principal.
    """
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-2.5-flash"):
        """
        Inicializa el modelo de chat Gemini.
        
        Args:
            api_key: API key de Google (o se toma de GOOGLE_API_KEY env)
            model_name: Nombre del modelo Gemini a usar
        """
        try:
            api_key = api_key or os.getenv("GOOGLE_API_KEY")
            
            if not api_key:
                logger.warning("GOOGLE_API_KEY no configurada, Gemini no disponible")
                self.llm = None
                return
            
            self.llm = ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=api_key,
                convert_system_message_to_human=True,
                temperature=0.7,
            )
            self.model_name = model_name
            logger.info(f"✅ Gemini LLM inicializado con modelo: {model_name}")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando Gemini LLM: {str(e)}")
            self.llm = None

    def ask(
        self,
        question: str,
        info_json: str = "{}",
        project_id: Optional[int] = None,
        tab: str = "general",
    ) -> str:
        """
        Hace una pregunta al chatbot Gemini.
        
        Args:
            question: Pregunta del usuario
            info_json: Información adicional en formato JSON
            project_id: ID del proyecto (opcional)
            tab: Componente MGA
            
        Returns:
            Respuesta del chatbot
        """
        if not self.llm:
            return "❌ Gemini LLM no está disponible. Verifica tu GOOGLE_API_KEY."
        
        try:
            template = PromptTemplate(
                template="""Eres un chatbot especializado en la Metodología General Ajustada (MGA) 
de Colombia para proyectos de inversión pública.

Información del proyecto: {info_json}

Pregunta del usuario: {question}

Respuesta:""",
                input_variables=["question", "info_json"]
            )
            
            chain = template | self.llm | StrOutputParser()
            response = chain.invoke({
                "question": question,
                "info_json": info_json
            })
            
            logger.info(f"✅ Respuesta generada por Gemini para tab={tab}")
            return response
            
        except Exception as e:
            logger.error(f"❌ Error en Gemini LLM: {str(e)}", exc_info=True)
            return "Lo siento, ocurrió un error al procesar tu pregunta."

    def reset_memory(self):
        """Nota: La memoria se gestiona desde la BD."""
        pass

