from ..config.config import LLM_CONFIG
from .mcp_client import MCPModel

def get_model(model_key: str = None):
    if not model_key:
        model_key = LLM_CONFIG["default"]

    model_config = LLM_CONFIG["models"].get(model_key)
    if not model_config:
        raise ValueError(f"Modelo '{model_key}' no está configurado.")

    provider = model_config["provider"]

    if provider == "mcp":
        return MCPModel(
            model_name=model_config["model_name"],
            server_url=model_config["server_url"],
            api_key=model_config.get("api_key")
        )
    else:
        raise ValueError(f"Proveedor '{provider}' no soportado.")
