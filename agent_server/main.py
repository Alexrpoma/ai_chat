# main.py

import asyncio
from contextlib import asynccontextmanager
import logging

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from agent_test import AgentService
from agents.mcp import MCPServerStreamableHttp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    phone_number: str
    party_id: int
    date: str
    prompt: str


class ChatResponse(BaseModel):
    response: str # html

lifespan_dependencies = {}


@asynccontextmanager
async def lifespan():

    logger.info("Application startup...")

    # 1. Iniciar el servidor MCP para que las herramientas del agente estén disponibles
    # mcp_server = MCPServerStreamableHttp(
    #     name="Streamable HTTP Python Server",
    #     params={"url": "http://localhost:8000/mcp"},  # Asegúrate de que este puerto esté libre
    # )

    # Ejecuta el servidor MCP en una tarea de fondo
    # mcp_task = asyncio.create_task(mcp_server.run())
    # logger.info("MCP Server task started.")

    # 2. Inicializar el servicio del agente y pasárle el servidor MCP
    agent = AgentService()
    # agent.initialize_agent(mcp_server)
    agent_mcp = await agent.streamable_http()

    # Almacenamos la instancia del agente para que esté disponible en los endpoints
    lifespan_dependencies["agent_service"] = agent

    yield  # La aplicación se ejecuta aquí

    # --- Código de apagado ---
    logger.info("Application shutdown...")
    agent_mcp.cancel()
    # try:
    #     await mcp_task
    # except asyncio.CancelledError:
    #     logger.info("MCP Server task successfully cancelled.")

    # Limpiar las dependencias
    lifespan_dependencies.clear()
    logger.info("Application shutdown complete.")


app = FastAPI(
    title="Alva Agent API",
    description="A REST API for interacting with the Alva AI Agent.",
    version="1.0.0",
    lifespan=lifespan
)


@app.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):

    agent_service = lifespan_dependencies.get("agent_service")
    if not agent_service:
        raise HTTPException(status_code=503, detail="Agent service is not available.")

    try:
        logger.info(f"Received prompt: '{request.prompt}'")
        agent_response = await agent_service.process_prompt(request.prompt)
        return ChatResponse(response=agent_response)
    except Exception as e:
        logger.error(f"An error occurred while processing the prompt: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal error occurred.")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)