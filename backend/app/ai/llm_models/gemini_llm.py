from typing import Optional
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI

from sqlalchemy.orm import Session
from app.models.chat_history import ChatHistory
from app.core.database import SessionLocal


class ChatBotModel:
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            convert_system_message_to_human=True
        )
        self.conversation: Optional[LLMChain] = None  # se inicializa más tarde

    def _init_chain(self, project_id: int = None, tab: str = None):
        """Inicializa la cadena con memoria y prompt si aún no existe."""
        if self.conversation is None:
            template = """Eres un chatbot que está capacitado para Formular proyectos de Inversión Pública,
            más precisamente en la Metodología General Ajustada (MGA) en Colombia.
            
            Conversación previa:
            {chat_history}

            Información adicional: {info_json}

            Nueva pregunta humana: {question}
            Respuesta:"""

            prompt = PromptTemplate.from_template(template)

            # Inicializar memoria vacía
            memory = ConversationBufferMemory(
                memory_key="chat_history",
                input_key="question",
                return_messages=True
            )

            # ⚡ Cargar historial previo desde BD si se tiene
            if project_id and tab:
                db: Session = SessionLocal()
                try:
                    history_records = (
                        db.query(ChatHistory)
                        .filter(ChatHistory.project_id == project_id, ChatHistory.tab == tab)
                        .order_by(ChatHistory.timestamp.asc())
                        .all()
                    )
                    # Agregar cada mensaje al buffer de memoria
                    for msg in history_records:
                        sender = "human" if msg.sender == "user" else "ai"
                        memory.chat_memory.add_message(msg.message)
                finally:
                    db.close()

            self.conversation = LLMChain(
                llm=self.llm,
                prompt=prompt,
                verbose=True,
                memory=memory
            )

    def ask(
        self,
        question: str,
        info_json: str = "{}",
        project_id: int = None,
        instance = None,
    ) -> str:
        """
        Hace una pregunta al chatbot y guarda el historial en la base de datos.
        """
        tab = instance.__tablename__ if instance else "general"
        self._init_chain(project_id, tab)

        # Generar respuesta usando la conversación
        response = self.conversation({
            "question": question,
            "info_json": info_json
        })
        bot_message = response["text"]

        # Guardar nuevo mensaje en BD
        db = SessionLocal()
        try:
            db.add(ChatHistory(project_id=project_id, tab=tab, sender="user", message=question))
            db.add(ChatHistory(project_id=project_id, tab=tab, sender="bot", message=bot_message))
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

        return bot_message

    def reset_memory(self):
        """Borra la memoria interna del LLM sin tocar la BD."""
        if self.conversation:
            self.conversation.memory.clear()
