# app/ai/main.py
from fastapi import APIRouter
from .models.mcp_client import MCPModel

router = APIRouter()

mcp_model = MCPModel(server_url="http://localhost:8001", api_key="mi_token_opcional")


@router.on_event("startup")
async def startup_event():
    await mcp_model.connect()


@router.on_event("shutdown")
async def shutdown_event():
    await mcp_model.close()


@router.post("/generate")
async def generate_text(prompt: str):
    response = await mcp_model.generate(prompt)
    return {"response": response}
