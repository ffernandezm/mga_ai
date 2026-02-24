"""
Configuración centralizada de la aplicación MGA.

Define constantes, validaciones y configuraciones globales.
"""

import os
import logging
from typing import List
from enum import Enum

logger = logging.getLogger(__name__)


class Environment(str, Enum):
    """Entornos soportados"""
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


class LLMProvider(str, Enum):
    """Proveedores de LLM disponibles"""
    GROQ = "groq"
    OLLAMA = "ollama"
    GEMINI = "gemini"
    HUGGINGFACE = "huggingface"


class MgaComponent(str, Enum):
    """Componentes de la Metodología General Ajustada"""
    PROBLEMS = "problems"
    PARTICIPANTS = "participants"
    POPULATION = "population"
    OBJECTIVES = "objectives"
    ALTERNATIVES = "alternatives"


class Config:
    """
    Configuración de la aplicación.
    
    Lee variables de entorno del archivo .env
    """
    
    # Aplicación
    APP_NAME = os.getenv("APP_NAME", "MGA Project Assistant API")
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    
    # Base de datos
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://ffernandez:123@localhost:5432/mga_db"
    )
    
    # LLM Configuration
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq").lower()
    
    # API Keys
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    
    # Groq Configuration
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    
    # Ollama Configuration
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    # RAG Configuration
    PDF_PATH = os.getenv(
        "PDF_PATH",
        "/home/ffernandez/mga_ai/backend/app/data/Documento_conceptual_2023.pdf"
    )
    EMBED_MODEL = os.getenv(
        "EMBED_MODEL",
        "sentence-transformers/all-MiniLM-L6-v2"
    )
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]
    
    @classmethod
    def get_allowed_origins(cls) -> List[str]:
        """Obtiene lista de orígenes permitidos para CORS"""
        if cls.ENVIRONMENT == "production":
            return cls.ALLOWED_ORIGINS
        else:
            return cls.ALLOWED_ORIGINS + ["*"]


# Instancia global de configuración
config = Config()


# Constantes
VALID_COMPONENTS = [component.value for component in MgaComponent]
VALID_LLM_PROVIDERS = [provider.value for provider in LLMProvider]

# Configuraciones por proveedor
LLM_PROVIDER_CONFIGS = {
    "groq": {
        "requires_api_key": True,
        "env_var": "GROQ_API_KEY",
        "model": config.GROQ_MODEL,
    },
    "gemini": {
        "requires_api_key": True,
        "env_var": "GOOGLE_API_KEY",
        "model": "gemini-2.5-flash",
    },
    "ollama": {
        "requires_api_key": False,
        "model": config.OLLAMA_MODEL,
        "base_url": config.OLLAMA_BASE_URL,
    },
    "huggingface": {
        "requires_api_key": False,
        "model": "gpt2",
    },
}


def validate_llm_configuration() -> bool:
    """
    Valida que la configuración del LLM actual es válida.
    
    Returns:
        bool: True si la configuración es válida
        
    Raises:
        ValueError: Si la configuración es inválida
    """
    provider_config = LLM_PROVIDER_CONFIGS.get(config.LLM_PROVIDER)
    
    if not provider_config:
        raise ValueError(f"Proveedor LLM no reconocido: {config.LLM_PROVIDER}")
    
    if provider_config.get("requires_api_key"):
        env_var = provider_config.get("env_var")
        api_key = os.getenv(env_var)
        
        if not api_key:
            logger.warning(
                f"⚠️ API Key requerida para {config.LLM_PROVIDER}. "
                f"Configura {env_var} en .env"
            )
            return False
    
    return True


def get_rag_config() -> dict:
    """
    Obtiene la configuración de RAG.
    
    Returns:
        dict: Configuración de RAG
    """
    return {
        "pdf_path": config.PDF_PATH,
        "embed_model": config.EMBED_MODEL,
        "chunk_size": 1000,
        "chunk_overlap": 200,
    }
