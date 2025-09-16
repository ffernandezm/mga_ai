from abc import ABC, abstractmethod

class LLMBase(ABC):
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """Generar texto a partir de un prompt"""
        pass
