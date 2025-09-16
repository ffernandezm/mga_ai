# mcp_client.py
import asyncio
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamablehttp_client


class MCPModel:
    def __init__(self, server_url: str, api_key: str = None):
        """
        Inicializa el cliente MCP.
        :param server_url: URL del servidor MCP.
        :param api_key: Token de autenticación (opcional).
        """
        self.server_url = server_url
        self.api_key = api_key
        self.session: ClientSession | None = None
        self._client_ctx = None  # contexto async
        self._connected = False

    async def connect(self):
        """Conecta con el servidor MCP y mantiene la sesión activa."""
        if self._connected:
            return self.session

        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        # Creamos el cliente como contexto manual
        self._client_ctx = streamablehttp_client(url=self.server_url, headers=headers)
        read_stream, write_stream, _ = await self._client_ctx.__aenter__()

        self.session = ClientSession(read_stream, write_stream)
        await self.session.initialize()
        self._connected = True

        return self.session

    async def close(self):
        """Cierra la sesión con el servidor MCP."""
        if self._connected and self._client_ctx:
            await self._client_ctx.__aexit__(None, None, None)
            self._connected = False
            self.session = None

    async def generate(self, prompt: str) -> str:
        """
        Envía un prompt al modelo MCP y devuelve la respuesta.
        """
        if not self._connected:
            await self.connect()

        response = await self.session.send_input(prompt)
        return response.get("output", "⚠️ No hubo respuesta del servidor MCP.")
