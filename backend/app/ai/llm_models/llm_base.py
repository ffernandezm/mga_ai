from abc import ABC, abstractmethod

class BaseLLM:
    async def generate_response(self, context, query):
        raise NotImplementedError