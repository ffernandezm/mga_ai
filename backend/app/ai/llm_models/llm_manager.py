"""
LLM Manager - Gestor centralizado de modelos de lenguaje.

Soporta múltiples proveedores (Groq, Gemini, etc) y gestiona
prompts dinámicos, historial de conversación y contexto del modelo.
"""

import os
import json
import logging
import re
from time import perf_counter
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.core.database import SessionLocal
from app.ai.rag import RAGManager
from app.ai.context.context_manager import ContextManager
from app.ai.llm_models.openai_llm import DEFAULT_OPENAI_MODEL, OPENAI_MODEL_PROFILES, resolve_openai_model
from app.ai.llm_models.token_diagnostics import PromptTokenReport, count_tokens
from sqlalchemy.orm import Session

# Configurar logging y cargar .env del root del backend de forma explícita
_ENV_PATH = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(dotenv_path=_ENV_PATH)
logger = logging.getLogger(__name__)

# Claves canónicas (ver app.ai.context.normalize_section) vs nombres de tabla
# legados usados directamente como `tab`. prompt_templates.json solo define
# contenido bajo las claves canónicas; estos aliases evitan duplicar prompts
# y mantienen compatibilidad si algo invoca `ask()`/`get_prompt_template()`
# todavía con el nombre de tabla legado.
_TEMPLATE_KEY_ALIASES = {
    "participants_general": "participants",
    "alternatives_general": "alternatives",
    "requirements_general": "requirements",
    "localization_general": "localization",
}


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
        """Inicializa el modelo LLM según la configuración del .env con LLM_PROVIDER"""
        self.llm_provider = os.getenv("LLM_PROVIDER", "groq").lower()
        self.templates = self._load_templates()
        self.rag_manager = RAGManager()
        self.context_manager = ContextManager()
        self.max_chat_history_messages = max(int(os.getenv("LLM_MAX_CHAT_HISTORY_MESSAGES", "6")), 1)
        self.max_project_context_chars = max(int(os.getenv("LLM_MAX_PROJECT_CONTEXT_CHARS", "12000")), 1000)
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
        elif self.llm_provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            configured_model = os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)

            if not api_key:
                raise ValueError("OPENAI_API_KEY no configurada en .env")

            model_name = resolve_openai_model(configured_model)
            model_usage = OPENAI_MODEL_PROFILES[model_name].usage

            logger.info(
                "Inicializando OpenAI LLM con modelo: %s (%s)",
                model_name,
                model_usage,
            )
            return ChatOpenAI(
                model=model_name,
                api_key=api_key,
                temperature=0.7,
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
            tab: Sección MGA. Acepta tanto los nombres de tabla legados
                (p. ej. "requirements_general", "localization_general") como
                las claves canónicas producidas por
                `app.ai.context.normalize_section` (p. ej. "requirements",
                "localization"). Ver `_TEMPLATE_KEY_ALIASES`.

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
        # Algunas claves canónicas (requirements, localization) no tienen
        # entrada propia en prompt_templates.json; reutilizan el prompt
        # especializado ya existente bajo el nombre legado de tabla.
        template_key = tab_key if tab_key in self.templates else _TEMPLATE_KEY_ALIASES.get(tab_key, tab_key)
        section_template = _strip_question_placeholder(
            self.templates.get(template_key, self.templates.get("default"))
        )

        if not section_template:
            section_template = _strip_question_placeholder(
                self.templates.get("default", "Responde de forma clara y concisa.")
            )

        # Regla solicitada: el prompt final debe ser general + sección.
        # Si la sección ya es "general", evitar duplicarla.
        if general_template and tab_key != "general":
            instruction_block = f"{general_template}\n\n{section_template}"
        else:
            instruction_block = section_template or general_template or "Responde de forma clara y concisa."

        template_text = (
            f"{instruction_block}\n\n"
            "=== INFORMACIÓN REGISTRADA DEL PROYECTO ===\n"
            "{project_context}\n\n"
            "=== CONTEXTO METODOLÓGICO MGA (RAG) ===\n"
            "{rag_context}\n\n"
            "=== HISTORIAL RECIENTE ===\n"
            "{chat_history}\n\n"
            "=== PREGUNTA DEL USUARIO ===\n"
            "{question}"
        )

        return PromptTemplate(
            template=template_text,
            input_variables=["project_context", "rag_context", "chat_history", "question"]
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
        
        # Usar una ventana pequeña para reducir latencia/tokens.
        for msg in chat_history[-self.max_chat_history_messages:]:
            sender = "Tú" if msg.get("sender") == "user" else "Yo"
            message_text = msg.get("message", "")[:400]  # Truncar mensajes largos
            context_lines.append(f"{sender}: {message_text}")
        
        context_lines.append("-" * 50)
        
        return "\n".join(context_lines)

    def _is_invoke_skipped(self) -> bool:
        """Permite desactivar llamadas al LLM durante debug para evitar consumo de tokens."""
        # Recarga .env para reflejar cambios recientes sin depender de reinicio del proceso.
        load_dotenv(dotenv_path=_ENV_PATH, override=True)

        # SKIP_LLM_INVOKE tiene prioridad solo si viene con valor no vacío.
        raw_skip = os.getenv("SKIP_LLM_INVOKE")
        raw_value = raw_skip if raw_skip is not None and raw_skip.strip() else os.getenv("DEBUG_SKIP_LLM_INVOKE", "false")
        return str(raw_value).strip().lower() in {"1", "true", "yes", "on"}

    def _merge_project_and_rag_context(self, project_context: str, rag_context: str) -> str:
        """DEPRECADO: ya no se usa en `ask()` (generaba RAG duplicado en el prompt,
        una vez dentro de `project_context` y otra en `{rag_context}`). Se
        conserva temporalmente por si algún consumidor externo la usa; el
        camino nuevo separa `project_context`/`rag_context` en
        `_prepare_contexts_for_prompt`.
        """
        project_context = self.context_manager.sanitize_context_text(project_context or "")
        rag_context = self.context_manager.sanitize_context_text(rag_context or "")

        if len(project_context) > self.max_project_context_chars:
            project_context = project_context[: self.max_project_context_chars]
        if len(rag_context) > self.max_project_context_chars:
            rag_context = rag_context[: self.max_project_context_chars]

        if project_context and rag_context:
            return (
                "Informacion del proyecto (BD):\n"
                f"{project_context}\n\n"
                f"Contexto recuperado (RAG):\n{rag_context}"
            )
        if rag_context:
            return rag_context
        return project_context

    def _prepare_contexts_for_prompt(self, project_context: str, rag_context: str) -> tuple[str, str]:
        """Sanitiza y trunca project_context/rag_context SIN mezclarlos.

        Mantiene ambos bloques separados en el prompt final
        (=== INFORMACIÓN REGISTRADA DEL PROYECTO === vs
        === CONTEXTO METODOLÓGICO MGA (RAG) ===), evitando la duplicación
        del contexto RAG que producía `_merge_project_and_rag_context`.
        """
        project_context = self.context_manager.sanitize_context_text(project_context or "")
        rag_context = self.context_manager.sanitize_context_text(rag_context or "")

        if len(project_context) > self.max_project_context_chars:
            project_context = project_context[: self.max_project_context_chars]
        if len(rag_context) > self.max_project_context_chars:
            rag_context = rag_context[: self.max_project_context_chars]

        return project_context, rag_context


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
        total_start = perf_counter()
        try:
            if self._is_invoke_skipped():
                logger.info(f"LLM invoke omitido por SKIP_LLM_INVOKE para tab={tab}, session={session_id}")
                return (
                    "[DEBUG] Llamada al modelo omitida (SKIP_LLM_INVOKE=true). "
                    "Desactiva esta variable para volver a consultar el LLM real."
                )

            # Obtener template
            prompt = self.get_prompt_template(tab)

            # Recuperar contexto RAG del documento conceptual según la pregunta.
            # `tab` (sección canónica) solo enriquece la consulta de retrieval;
            # la pregunta que recibe el LLM no se modifica.
            rag_start = perf_counter()
            rag_context = self.rag_manager.get_relevant_context(question, section=tab)
            rag_ms = (perf_counter() - rag_start) * 1000
            # project_context y rag_context viajan SEPARADOS al prompt (no se
            # mezclan): el proyecto es responsabilidad de ContextManager y el
            # RAG de RAGManager, cada uno bajo su propia etiqueta.
            project_context, rag_context = self._prepare_contexts_for_prompt(context, rag_context)

            # Crear cadena LLM
            chain = prompt | self.model | StrOutputParser()
            llm_start = perf_counter()
            response = chain.invoke({
                "project_context": project_context,
                "rag_context": rag_context,
                "chat_history": self._build_chat_context(chat_history) if chat_history else "",
                "question": question,
            })
            llm_ms = (perf_counter() - llm_start) * 1000
            total_ms = (perf_counter() - total_start) * 1000
            
            logger.info(
                f"Respuesta generada para tab={tab}, session={session_id}, "
                f"con historial={bool(chat_history)}, con datos={bool(project_context)}, con rag={bool(rag_context)}"
            )
            logger.info(
                "⏱️ LLM timing | tab=%s session=%s rag_ms=%.1f llm_ms=%.1f total_ms=%.1f "
                "question_chars=%s context_chars=%s rag_chars=%s",
                tab,
                session_id,
                rag_ms,
                llm_ms,
                total_ms,
                len(question or ""),
                len(project_context or ""),
                len(rag_context or ""),
            )
            return response
            
        except Exception as e:
            total_ms = (perf_counter() - total_start) * 1000
            logger.error("⏱️ LLM timing fallo | tab=%s session=%s total_ms=%.1f", tab, session_id, total_ms)
            logger.error(f"Error en LLM ({tab}): {str(e)}", exc_info=True)
            return "Lo siento, ocurrió un error al procesar tu pregunta. Intenta de nuevo."

    def measure_prompt_tokens(
        self,
        question: str,
        tab: str = "general",
        context: str = "",
        chat_history: list = None,
    ) -> PromptTokenReport:
        """Diagnóstico dev/test: mide el tamaño real del prompt SIN invocar al proveedor.

        Reutiliza exactamente las mismas piezas que `ask()` (template,
        recuperación RAG, historial) para que la medición refleje el prompt
        real que se enviaría. No trunca nada: solo mide. Ver
        `token_diagnostics.TOKEN_METHOD` para el método de conteo.
        """
        prompt = self.get_prompt_template(tab)
        rag_context_raw = self.rag_manager.get_relevant_context(question, section=tab)
        project_context, rag_context = self._prepare_contexts_for_prompt(context, rag_context_raw)
        history_text = self._build_chat_context(chat_history) if chat_history else ""

        # El "system"/instrucciones es la parte del template anterior al primer
        # bloque de contexto (general + sección ya combinados por get_prompt_template).
        system_text = prompt.template.split("=== INFORMACIÓN REGISTRADA DEL PROYECTO ===")[0]

        system_tokens = count_tokens(system_text)
        project_context_tokens = count_tokens(project_context)
        rag_context_tokens = count_tokens(rag_context)
        history_tokens = count_tokens(history_text)
        question_tokens = count_tokens(question)

        return PromptTokenReport(
            section=tab,
            system_tokens=system_tokens,
            project_context_tokens=project_context_tokens,
            rag_context_tokens=rag_context_tokens,
            history_tokens=history_tokens,
            question_tokens=question_tokens,
            estimated_total_tokens=(
                system_tokens + project_context_tokens + rag_context_tokens + history_tokens + question_tokens
            ),
        )

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
            logger.error(f"Error validando configuración: {str(e)}")
            return False

