from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI

class ChatBotModel:
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            convert_system_message_to_human=True
        )

        template = """Eres un chatbot que está capacitado para Formular proyectos de Inversión Pública,
        más precisamente en la Metodología General Ajustada (MGA) en Colombia.
        
        Te encargarás de ayudar a resolver el árbol de problemas y esta es la información que se tiene actualmente:
        {info_json}
        
        Conversación previa:
        {chat_history}

        Nueva pregunta humana: {question}
        Respuesta:"""

        prompt = PromptTemplate.from_template(template)

        # ⚡️ Clave: decirle que solo "question" es la variable que se guarda en memoria
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            input_key="question"
        )

        self.conversation = LLMChain(
            llm=self.llm,
            prompt=prompt,
            verbose=True,
            memory=memory
        )

    def ask(self, question: str, info_json: str = "{}") -> str:
        response = self.conversation({
            "question": question,
            "info_json": info_json
        })
        return response["text"]

    def reset_memory(self):
        self.conversation.memory.clear()
