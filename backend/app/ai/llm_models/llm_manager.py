"""
LLM Manager - Gestor centralizado de modelos de lenguaje.

Soporta múltiples proveedores (Groq, Gemini, etc) y gestiona
prompts dinámicos, historial de conversación y contexto del modelo.
"""

import os
import json
import logging
import re
from typing import Optional
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.core.database import SessionLocal
from sqlalchemy.orm import Session

# Configurar logging
load_dotenv()
logger = logging.getLogger(__name__)

# ==============================
# 🔹 DEPENDENCIA DB
# ==============================
def get_db():
    """Dependencia para obtener sesión de BD."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==============================
# 🔹 CLASE PRINCIPAL DEL LLM
# ==============================
class LLMManager:
    """
    Gestor centralizado de LLMs.
    
    Soporta Groq, Gemini y otros proveedores.
    Gestiona prompts dinámicos y contexto del modelo.
    """
    
    def __init__(self):
        """Inicializa el modelo LLM según la configuración del .env"""
        self.llm_provider = os.getenv("LLM_PROVIDER", "groq").lower()
        self.templates = self._load_templates()
        self.model = self._initialize_llm()
        logger.info(f"✅ LLMManager inicializado con provider: {self.llm_provider}")

    def _initialize_llm(self):
        """Inicializa el modelo LLM según el provider configurado."""
        if self.llm_provider == "groq":
            api_key = os.getenv("GROQ_API_KEY")
            model_name = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
            
            if not api_key:
                raise ValueError("GROQ_API_KEY no configurada en .env")
            
            logger.info(f"Inicializando Groq LLM con modelo: {model_name}")
            return ChatGroq(
                model_name=model_name,
                groq_api_key=api_key,
                temperature=0.7,
            )
            
        elif self.llm_provider == "gemini":
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY no configurada en .env")
            
            logger.info("Inicializando Gemini LLM")
            return ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                google_api_key=api_key,
                convert_system_message_to_human=True,
            )
        else:
            raise ValueError(f"LLM Provider no soportado: {self.llm_provider}")

    def _load_templates(self) -> dict:
        """Carga los templates desde un archivo JSON."""
        data_path = os.path.join(os.path.dirname(__file__), "../data/prompt_templates.json")
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                templates = json.load(f)
                logger.info(f"✅ {len(templates)} templates cargados")
                return templates
        except Exception as e:
            logger.warning(f"⚠️ Error cargando templates: {e}")
            return {
                "default": "Eres un asistente útil para proyectos de inversión pública MGA. Responde de forma clara y concisa."
            }

    def get_prompt_template(self, tab: str) -> PromptTemplate:
        """
        Obtiene la plantilla de prompt para un componente MGA.
        
        Args:
            tab: Componente MGA (problems, participants, population, etc)
            
        Returns:
            PromptTemplate configurado
        """
        def _strip_question_placeholder(template_value: str) -> str:
            """Elimina placeholders heredados de pregunta para evitar duplicidades."""
            if not template_value:
                return ""
            # Remueve líneas tipo: "Pregunta: {question}" o "Pregunta del usuario: {question}"
            cleaned = re.sub(
                r"(?im)^\s*Pregunta(?:\s+del\s+usuario)?\s*:\s*\{question\}\s*$",
                "",
                template_value,
            )
            return cleaned.strip()

        tab_key = (tab or "general").lower()
        general_template = _strip_question_placeholder(self.templates.get("general", ""))
        module_template = _strip_question_placeholder(
            self.templates.get(tab_key, self.templates.get("default"))
        )

        if not module_template:
            module_template = _strip_question_placeholder(
                self.templates.get("default", "Responde de forma clara y concisa.")
            )

        # Regla solicitada: el prompt final debe ser general + módulo.
        # Si el módulo ya es "general", evitar duplicarlo.
        if general_template and tab_key != "general":
            instruction_block = f"{general_template}\n\n{module_template}"
        else:
            instruction_block = module_template or general_template or "Responde de forma clara y concisa."

        template_text = (
            f"{instruction_block}\n\n"
            "Informacion del proyecto:\n"
            "{project_context}\n\n"
            "Contexto de la conversacion:\n"
            "{chat_history}\n\n"
            "Pregunta del usuario:\n"
            "{question}"
        )
        
        return PromptTemplate(
            template=template_text,
            input_variables=["project_context", "chat_history", "question"]
        )

    def _build_chat_context(self, chat_history: list) -> str:
        """
        Construye el contexto del historial de chat de forma natural.
        
        Args:
            chat_history: Lista de mensajes anteriores
            
        Returns:
            Contexto formateado del historial
        """
        if not chat_history:
            return ""
        
        context_lines = []
        context_lines.append("Contexto de la conversación anterior:")
        context_lines.append("-" * 50)
        
        # Usar últimos 8 mensajes para no exceder límite
        for msg in chat_history[-8:]:
            sender = "Tú" if msg.get("sender") == "user" else "Yo"
            message_text = msg.get("message", "")[:400]  # Truncar mensajes largos
            context_lines.append(f"{sender}: {message_text}")
        
        context_lines.append("-" * 50)
        
        return "\n".join(context_lines)

    def _is_invoke_skipped(self) -> bool:
        """Permite desactivar llamadas al LLM durante debug para evitar consumo de tokens."""
        raw_value = os.getenv("SKIP_LLM_INVOKE", os.getenv("DEBUG_SKIP_LLM_INVOKE", "true"))
        #raw_value = "false"
        return str(raw_value).strip().lower() in {"1", "true", "yes", "on"}


    def ask(
        self,
        question: str,
        tab: str = "general",
        context: str = "",
        chat_history: list = None,
        session_id: str = None,
    ) -> str:
        """
        Invoca el LLM con la pregunta, contexto e historial de chat.
        
        Args:
            question: Pregunta del usuario
            tab: Componente MGA para usar template específico
            context: Contexto adicional (datos del modelo)
            chat_history: Historial de mensajes anteriores de la conversación
            session_id: ID de sesión (opcional, para tracking)
            
        Returns:
            Respuesta del LLM
        """
        try:
            if self._is_invoke_skipped():
                logger.info(f"⏭️ LLM invoke omitido por SKIP_LLM_INVOKE para tab={tab}, session={session_id}")
                return (
                    "[DEBUG] Llamada al modelo omitida (SKIP_LLM_INVOKE=true). "
                    "Desactiva esta variable para volver a consultar el LLM real."
                )

            # Obtener template
            prompt = self.get_prompt_template(tab)
            
            # Crear cadena LLM
            chain = prompt | self.model | StrOutputParser()
            
            response = chain.invoke({
                "project_context": context or "",
                "chat_history": self._build_chat_context(chat_history) if chat_history else "",
                "question": question,
            })
            
            logger.info(f"✅ Respuesta generada para tab={tab}, session={session_id}, con historial={bool(chat_history)}, con datos={bool(context)}")
            return response
            
        except Exception as e:
            logger.error(f"❌ Error en LLM ({tab}): {str(e)}", exc_info=True)
            return "Lo siento, ocurrió un error al procesar tu pregunta. Intenta de nuevo."

    def validate_configuration(self) -> bool:
        """Valida que el LLM esté correctamente configurado."""
        try:
            if self._is_invoke_skipped():
                logger.info("⏭️ Validación LLM omitida por SKIP_LLM_INVOKE")
                return True

            # Probar una invocación simple
            test_response = self.ask(
                question="Test",
                tab="general",
                context="Testing configuration",
                chat_history=None
            )
            return bool(test_response)
        except Exception as e:
            logger.error(f"❌ Error validando configuración: {str(e)}")
            return False

