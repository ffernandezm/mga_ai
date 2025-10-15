import uuid
import psycopg
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_postgres import PostgresChatMessageHistory

# Importa tu función personalizada para guardar mensajes en la tabla personalizada
from app.models.chat_history import save_chat_message

# === CONFIGURACIÓN DEL MODELO ===
model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key="AIzaSyAze2dhiNBl59FKZPRdPtvfXomwOPxG6rw",
    convert_system_message_to_human=True
)

# === PROMPT ===
human_template = "{question}"
prompt_template = ChatPromptTemplate.from_messages(
    [
        MessagesPlaceholder(variable_name="history"),
        ("human", human_template),
    ]
)

chain = prompt_template | model

# === TABLA EN POSTGRES ===
table_name = "chat_history"

# === CONFIGURACIÓN DE SESIÓN ===
def get_by_session_id(session_id: str) -> BaseChatMessageHistory:
    sync_connection = psycopg.connect(
        dbname="postgres",
        user="postgres",
        password="ffernandez",
        host="localhost",
        port="5432"
    )

    # ⚠️ OJO: Esto crea una tabla "chat_history" si no existe,
    # pero no puede manejar tus columnas extra (project_id, tab, sender)
    # Así que solo la usamos como base para el historial.
    return PostgresChatMessageHistory(
        table_name=table_name,
        session_id=session_id,
        sync_connection=sync_connection,
    )

chain_with_history = RunnableWithMessageHistory(
    chain,
    get_by_session_id,
    input_messages_key="question",
    history_messages_key="history",
)

# === VARIABLES DE CONTEXTO ===
fixed_session_id = str(uuid.uuid4())
project_id = 1              # Cambia esto según tu proyecto real
tab = "problems"            # Cambia al módulo actual ("participants", "objectives", etc.)

# === LOOP DE CONVERSACIÓN ===
while True:
    user_question = input(">>> ")
    if user_question.lower() in {"exit", "salir", "quit"}:
        print("👋 Saliendo del chat...")
        break

    # Guarda el mensaje del usuario
    save_chat_message(project_id, tab, "user", user_question)

    # Llama al modelo
    result = chain_with_history.invoke(
        {"question": user_question},
        config={"configurable": {"session_id": fixed_session_id}},
    )

    # Guarda la respuesta del bot
    save_chat_message(project_id, tab, "bot", result.content)

    print(result.content)
