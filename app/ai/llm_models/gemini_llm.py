from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
from ..config.config import GOOGLE_API_KEY
from ..llm_models.llm_base import BaseLLM

class GeminiLLM(BaseLLM):
    def __init__(self):
        self.model = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=GOOGLE_API_KEY,
            convert_system_message_to_human=True
        )

    async def generate_response(self, context, query):
        prompt = f"Usando el siguiente contexto y lo que tengas en tu conocimiento actual sobre Metodología general ajustable (MGA), responde la pregunta:\n\n{context}\n\nPregunta: {query}"
        response = await self.model.agenerate([[HumanMessage(content=prompt)]])
        return response.generations[0][0].text