import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
#OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") Cuando se tenga GPT

LLM_CONFIG = {
    "default": "gemini",  # Modelo principal por defecto
    "models": {
        "gemini": {
            "provider": "mcp",
            "server_url": "https://mcp.gemini-server.com",
            "api_key": "AIzaSyD-KdhA56Pemuj_WDOO_WeP2YTLVBrHO7c",
            "model_name": "gemini-1.5-pro"
        },
        "openai": {
            "provider": "mcp",
            "server_url": "https://mcp.openai-server.com",
            "api_key": "API_KEY_OPENAI",
            "model_name": "gpt-4o"
        },
        "local-llm": {
            "provider": "mcp",
            "server_url": "http://localhost:8001",  # Ejemplo de un servidor MCP local
            "api_key": None,
            "model_name": "llama-3-8b-instruct"
        }
    }
}
