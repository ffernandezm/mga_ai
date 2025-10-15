from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_postgres import PostgresChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from app.core.database import DATABASE_URL
import psycopg

class LLMManager:
    def __init__(self):
        self.model = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key="AIzaSyAze2dhiNBl59FKZPRdPtvfXomwOPxG6rw",
            convert_system_message_to_human=True,
        )

        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", "Eres un asistente útil. Responde de forma clara y concisa."),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{question}"),
        ])

        self.chain = self.prompt_template | self.model

        self.chain_with_history = RunnableWithMessageHistory(
            self.chain,
            self.get_by_session_id,
            input_messages_key="question",
            history_messages_key="history",
        )

    def get_by_session_id(self, session_id: str):
        # Crear conexión activa
        sync_connection = psycopg.connect(DATABASE_URL)

        # Inicializar historial LLM usando **argumentos posicionales**
        return PostgresChatMessageHistory(
            "chat_history_",  # table_name → primer argumento posicional
            session_id,      # session_id → segundo argumento posicional
            sync_connection=sync_connection  # sync_connection → keyword
        )

    def ask(self, question: str, session_id: str) -> str:
        try:
            result = self.chain_with_history.invoke(
                {"question": question},
                config={"configurable": {"session_id": session_id}},
            )
            return result.content
        except Exception as e:
            print(f"Error en LLM: {e}")
            return "Lo siento, ocurrió un error al procesar tu pregunta."
