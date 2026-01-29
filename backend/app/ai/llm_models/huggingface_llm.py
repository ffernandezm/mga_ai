"""
Modelo LLM usando HuggingFace (Modelos gratuitos sin API key)

Requisitos:
1. Instalar: pip install transformers torch (requiere GPU para mejor rendimiento)
2. Los modelos se descargan automáticamente de HuggingFace

Modelos recomendados (ligeros y rápidos):
- "gpt2": Ultra ligero, pero básico
- "distilgpt2": Muy rápido, buen balance
- "meta-llama/Llama-2-7b-chat": Potente pero grande (~15GB)
- "mistralai/Mistral-7B-Instruct-v0.1": Excelente calidad-velocidad
- "tiiuae/falcon-7b-instruct": Muy bueno
"""

from langchain_huggingface import HuggingFacePipeline
from transformers import pipeline
import torch


class HuggingFaceLLM:
    def __init__(self, model_name: str = "gpt2", use_gpu: bool = True):
        """
        Inicializa el modelo HuggingFace local
        
        Args:
            model_name: ID del modelo en HuggingFace Hub
            use_gpu: Usar GPU si está disponible
        """
        try:
            device = 0 if (use_gpu and torch.cuda.is_available()) else -1
            device_str = "CUDA" if device == 0 else "CPU"
            print(f"Usando dispositivo: {device_str}")
            
            # Crear pipeline de texto
            hf_pipeline = pipeline(
                "text-generation",
                model=model_name,
                device=device,
                model_kwargs={"torch_dtype": torch.float16 if device == 0 else torch.float32},
                max_new_tokens=512,
            )
            
            self.model = HuggingFacePipeline(
                model_id=model_name,
                task="text-generation",
                model_kwargs={"torch_dtype": torch.float16 if device == 0 else torch.float32},
                pipeline_kwargs={"max_new_tokens": 512},
            )
            self.model_name = model_name
            self.is_available = True
            
        except Exception as e:
            print(f"⚠️ Error inicializando HuggingFace LLM: {e}")
            print("💡 Instala las dependencias: pip install transformers torch")
            self.is_available = False
            self.model = None

    def get_model(self):
        """Retorna el modelo LLM"""
        if not self.is_available:
            raise RuntimeError("HuggingFace LLM no está disponible.")
        return self.model
