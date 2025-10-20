from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_postgres import PostgresChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from app.models.get_table_data import get_table_data
from app.core.database import DATABASE_URL, SessionLocal
from sqlalchemy.orm import Session
from fastapi import Depends
import psycopg
import json
import os

# ==============================
# 🔹 DEPENDENCIA DB
# ==============================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==============================
# 🔹 CLASE PRINCIPAL DEL LLM
# ==============================
class LLMManager:
    def __init__(self):
        """Inicializa el modelo LLM y carga los templates"""
        self.model = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key="AIzaSyCARWRLWZHWNXKMycb5o1gtqAVnA86IgF8",
            convert_system_message_to_human=True,
        )
        self.templates = self._load_templates()

    # ------------------------------
    # CARGA DE PROMPTS DESDE ARCHIVO
    # ------------------------------
    def _load_templates(self):
        """Carga los templates desde un archivo JSON"""
        data_path = os.path.join(os.path.dirname(__file__), "../data/prompt_templates.json")
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Error cargando templates: {e}")
            return {"default": "Eres un asistente útil. Responde de forma clara y concisa."}

    # ------------------------------
    # CONSTRUCCIÓN DEL PROMPT DINÁMICO
    # ------------------------------
    def get_prompt_template(self, tab: str, project_id: int, db: Session):
        """
        Crea el prompt dinámico según el módulo/tab.
        Integra tanto la plantilla base como los datos reales del modelo.
        """
        prompt_text = self.templates.get(tab.lower(), self.templates.get("default"))

        # Obtener los datos actuales del modelo
        try:
            table_data = get_table_data(tab, project_id, db)
            dict_data_model = table_data.get("data", [{}])[0] if table_data else {}
        except Exception as e:
            print(f"⚠️ Error al obtener datos del modelo ({tab}): {e}")
            dict_data_model = {}

        # Convertir los datos del modelo en formato JSON legible para el prompt
        model_context = json.dumps(dict_data_model, ensure_ascii=False, indent=2)
        
        # Escapar llaves para que LangChain no las trate como variables
        model_context = model_context.replace("{", "{{").replace("}", "}}")

        # Incluir el contexto del modelo directamente en el mensaje del sistema
        full_prompt = (
            f"{prompt_text}\n\n"
            f"A continuación tienes la información registrada del modelo '{tab}':\n"
            f"{model_context}\n\n"
            f"Usa esta información como contexto al responder preguntas del usuario."
        )

        return ChatPromptTemplate.from_messages([
            ("system", full_prompt),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{question}"),
        ])

    # ------------------------------
    # HISTORIAL DE CONVERSACIÓN
    # ------------------------------
    def get_by_session_id(self, session_id: str) -> BaseChatMessageHistory:
        """Crea o recupera el historial de conversación en Postgres"""
        sync_connection = psycopg.connect(DATABASE_URL)
        return PostgresChatMessageHistory(
            "chat_history_",
            session_id,
            sync_connection=sync_connection,
        )

    # ------------------------------
    # FUNCIÓN PRINCIPAL DE CONSULTA
    # ------------------------------
    def ask(self, question: str, session_id: str, tab: str, project_id: int, db: Session) -> str:
        """
        Envía la pregunta al modelo, incluyendo el historial y contexto del modelo.
        """
        try:
            # Construir el prompt dinámico
            prompt_template = self.get_prompt_template(tab, project_id, db)
            chain = prompt_template | self.model

            # Agregar historial de conversación
            chain_with_history = RunnableWithMessageHistory(
                chain,
                self.get_by_session_id,
                input_messages_key="question",
                history_messages_key="history",
            )

            # Ejecutar la pregunta con sesión persistente
            result = chain_with_history.invoke(
                {"question": question},
                config={"configurable": {"session_id": session_id}},
            )

            return result.content

        except Exception as e:
            print(f"Error en LLM ({tab}): {e}")
            return "Lo siento, ocurrió un error al procesar tu pregunta."
