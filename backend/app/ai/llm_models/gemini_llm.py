from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI
from sqlalchemy.orm import Session

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

    def ask(
        self,
        question: str,
        info_json: str = "{}",
        instance=None,
        db: Session = None
        ) -> dict:
        """
        Hace una pregunta al chatbot.
        - Si se pasa un `instance` (cualquier modelo con atributo chat_history) y un `db`,
          guarda el historial en la base de datos.
        - Si no, solo devuelve la respuesta.
        """
        response = self.conversation({
            "question": question,
            "info_json": info_json
        })

        result = {
            "user": question,
            "bot": response["text"]
        }

        # Guardar historial si se pasa un modelo con atributo chat_history
        if instance is not None and db is not None:
            if not hasattr(instance, "chat_history"):
                raise AttributeError(
                    f"El modelo {instance.__class__.__name__} no tiene campo 'chat_history'"
                )
            history = instance.chat_history or []
            history.append(result)
            instance.chat_history = history
            db.add(instance)
            db.commit()
            db.refresh(instance)

        return result['bot']

    def reset_memory(self):
        self.conversation.memory.clear()
