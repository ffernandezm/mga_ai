"""
Modelo LLM usando Ollama (Modelos locales gratuitos)

Requisitos previos:
1. Descargar e instalar Ollama desde: https://ollama.ai
2. Ejecutar: ollama pull mistral (o neural-chat, llama2, etc.)
3. Ejecutar: ollama serve (en otra terminal)

Modelos disponibles (gratuitos y rápidos):
- mistral: 7B, muy rápido y preciso
- neural-chat: 7B, optimizado para chat
- llama2: 7B o 13B, muy completo
- orca-mini: 3B, super ligero
- dolphin-mixtral: 8x7B, muy potente (necesita GPU)
"""

from langchain_ollama import ChatOllama
from langchain_core.chat_history import BaseChatMessageHistory
import socket


def is_ollama_running(base_url: str = "http://localhost:11434") -> bool:
    """
    Verifica si Ollama está corriendo
    """
    try:
        # Intentar conectar al puerto 11434
        host = base_url.split("://")[1].split(":")[0]
        port = int(base_url.split(":")[-1])
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False


class OllamaLLM:
    def __init__(self, model_name: str = "mistral", base_url: str = "http://localhost:11434"):
        """
        Inicializa el modelo Ollama local
        
        Args:
            model_name: Nombre del modelo (mistral, neural-chat, llama2, etc.)
            base_url: URL donde corre el servidor Ollama
        """
        self.model_name = model_name
        self.base_url = base_url
        self.is_available = False
        self.model = None
        
        # Verificar si Ollama está disponible
        if not is_ollama_running(base_url):
            print(f"⚠️  Ollama no está corriendo en {base_url}")
            print("💡 Ejecuta en otra terminal: ollama serve")
            return
        
        try:
            self.model = ChatOllama(
                model=model_name,
                base_url=base_url,
                temperature=0.7,
                top_p=0.9,
            )
            self.is_available = True
            print(f"✅ Ollama conectado: {model_name}")
        except Exception as e:
            print(f"⚠️  Error inicializando Ollama: {e}")
            print(f"💡 Asegúrate de tener el modelo: ollama pull {model_name}")

    def get_model(self):
        """Retorna el modelo LLM"""
        if not self.is_available:
            raise RuntimeError(
                f"Ollama no está disponible. "
                f"Ejecuta 'ollama serve' en otra terminal y asegúrate de tener el modelo: "
                f"ollama pull {self.model_name}"
            )
        return self.model

