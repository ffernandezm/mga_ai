import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

API_KEY = ""

llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.7)

promt = ChatPromptTemplate.from_messages([
    MessagesPlaceholder(variable_name="chat_history"),
    ("human","{input}")
    ])


# Crear cadena de conversación

chain = promt | llm


def ejecutar_chatbot():
    print("Bienvenido a mi chatbot con LangChain")