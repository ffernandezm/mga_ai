"""
Modelo LLM usando Groq (API gratuita, MUY rápida)

Requisitos:
1. Crear cuenta gratuita en: https://console.groq.com
2. Copiar tu API key
3. Configurar variable de entorno: GROQ_API_KEY

Ventajas:
- API gratuita con cuota generosa
- EXTREMADAMENTE rápida (50+ tokens/segundo)
- Modelos potentes: Mixtral, Llama2, Gemma
- No requiere GPU local
"""

from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()


class GroqLLM:
    def __init__(self, model_name: str = "llama-3.1-8b-instant", api_key: str = None):
        """
        Inicializa el modelo Groq (API gratuita y muy rápida)
        
        Args:
            model_name: Modelo a usar (llama-3.1-8b-instant, deepseek-r1-distill-llama-70b, etc.)
            api_key: Tu API key de Groq (o se toma de GROQ_API_KEY env)
        """
        try:
            api_key = api_key or os.getenv("GROQ_API_KEY")
            
            if not api_key:
                raise ValueError(
                    "⚠️ GROQ_API_KEY no configurada. "
                    "Obtén una en https://console.groq.com y configúrala en .env"
                )
            
            self.model = ChatGroq(
                model_name=model_name,
                groq_api_key=api_key,
                temperature=0.7,
            )
            self.model_name = model_name
            self.is_available = True
            print(f"✅ Groq LLM inicializado con modelo: {model_name}")
            
        except Exception as e:
            print(f"⚠️ Error inicializando Groq LLM: {e}")
            self.is_available = False
            self.model = None

    def get_model(self):
        """Retorna el modelo LLM"""
        if not self.is_available:
            raise RuntimeError(
                "Groq LLM no está disponible. "
                "Verifica tu API key en GROQ_API_KEY."
            )
        return self.model
