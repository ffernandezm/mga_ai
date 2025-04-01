from .document import Document
from ..llm_models.gemini_llm import GeminiLLM

class QueryProcessor:
    def __init__(self, context):
        self.llm_model = GeminiLLM()
        self.context = context

    async def ask(self, query):
        return await self.llm_model.generate_response(self.context, query)