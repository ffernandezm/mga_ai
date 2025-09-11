from .document import Document
from ..llm_models.gemini_llm import ChatBotModel

class QueryProcessor:
    def __init__(self, context):
        self.llm_model = ChatBotModel()
        self.context = context

    async def ask(self, query):
        return await self.llm_model.generate_response(self.context, query)