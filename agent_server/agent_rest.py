import configparser
import json
import re
import asyncio

import tiktoken
from agents import OpenAIChatCompletionsModel, ModelSettings, Runner, Agent, set_tracing_disabled
from agents.mcp import MCPServer, MCPServerStreamableHttp
from openai import AsyncOpenAI


from fastapi import FastAPI, Request
from pydantic import BaseModel, Field
from typing import List, Dict, Any


def save_history_to_file(history, filename="chat_history.txt"):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(json.dumps(history, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"⚠️ Error saving history: {e}")


def clean_assistant_response(response_text: str) -> str:
    pattern = r"<think>.*?</think>"
    cleaned_text = re.sub(pattern, "", response_text, flags=re.DOTALL)
    return cleaned_text.strip()


# ## NUEVO ## - Modelos Pydantic para la API
class ChatRequest(BaseModel):
    prompt: str
    # El historial de chat ahora se pasa en cada petición
    history: List[Dict[str, Any]] = Field(default_factory=list)


class ChatResponse(BaseModel):
    response: str
    history: List[Dict[str, Any]]


class AgentService:
    def __init__(self, mcp_server: MCPServer):

        self.mcp_server = mcp_server

        config = configparser.ConfigParser()
        config.read('config.ini')
        llm_url = config.get("LLM", "URL")
        api_key = config.get("LLM", "API_KEY")
        self.__model_name = config.get("LLM", "MODEL")
        self.__client = AsyncOpenAI(base_url=llm_url, api_key=api_key)

        self.__instructions = f"""You are Alva..."""

        self.MAX_CONTEXT_TOKENS = 2048
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def count_tokens_for_message(self, message: dict) -> int:
        num_tokens = 4
        for key, value in message.items():
            if value:
                num_tokens += len(self.tokenizer.encode(str(value)))
        return num_tokens

    def truncate_history(self, chat_history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        current_tokens = sum(self.count_tokens_for_message(msg) for msg in chat_history)

        if current_tokens <= self.MAX_CONTEXT_TOKENS:
            return chat_history

        print(f"Current tokens ({current_tokens}) exceed the limit ({self.MAX_CONTEXT_TOKENS}). Truncating...")

        system_prompt = chat_history[0]
        conversation = chat_history[1:]

        while current_tokens > self.MAX_CONTEXT_TOKENS and len(conversation) > 2:

            removed_user = conversation.pop(0)
            removed_assistant = conversation.pop(0)
            current_tokens -= (self.count_tokens_for_message(removed_user) +
                               self.count_tokens_for_message(removed_assistant))

        print(f"History truncated. Final token count: ~{current_tokens}")
        return [system_prompt] + conversation

    async def process_request(self, request: ChatRequest) -> ChatResponse:
        set_tracing_disabled(disabled=True)

        agent = Agent(
            name="Alva",
            model=OpenAIChatCompletionsModel(model=self.__model_name, openai_client=self.__client),
            mcp_servers=[self.mcp_server],
            model_settings=ModelSettings(tool_choice="auto", temperature=0.1),
            tool_use_behavior="stop_on_first_tool"
        )

        if not request.history:
            chat_history = [{"role": "system", "content": self.__instructions}]
        else:
            chat_history = request.history

        chat_history.append({"role": "user", "content": request.prompt})

        # Trunk history
        chat_history = self.truncate_history(chat_history)

        save_history_to_file(chat_history, "api_chat_history.txt")

        result = await Runner.run(starting_agent=agent, input=chat_history)

        final_response_text = "Error: Could not process the request."

        if result and result.final_output:
            output_string = result.final_output
            try:
                first_level_data = json.loads(output_string)
                if isinstance(first_level_data, dict) and 'text' in first_level_data:
                    json_string_from_text_key = first_level_data['text']
                    second_level_data = json.loads(json_string_from_text_key)
                    if isinstance(second_level_data, dict) and 'html' in second_level_data:
                        final_response_text = second_level_data['html']
            except (json.JSONDecodeError, TypeError):
                final_response_text = clean_assistant_response(output_string)

        chat_history.append({"role": "assistant", "content": final_response_text})

        return ChatResponse(response=final_response_text, history=chat_history)


app = FastAPI(title="Alva Agent Service")


@app.on_event("startup")
async def startup_event():
    print("Starting up and connecting to MCP Server...")
    mcp_client = MCPServerStreamableHttp(
        name="Streamable HTTP Python Server",
        params={"url": "http://localhost:8000/mcp"},
    )

    app.state.mcp_server = await mcp_client.__aenter__()
    app.state.agent_service = AgentService(mcp_server=app.state.mcp_server)
    print("Agent service initialized.")


@app.on_event("shutdown")
async def shutdown_event():
    print("Shutting down and cleaning up MCP connection...")
    await app.state.mcp_server.__aexit__(None, None, None)



@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Receives a user prompt and chat history, processes it with the Alva agent,
    and returns the response along with the updated history.
    """
    agent_service = app.state.agent_service
    return await agent_service.process_request(request)


@app.get("/")
def read_root():
    return {"message": "Alva Agent Service is running. Use the /chat endpoint to interact."}


if __name__ == "__main__":
    import uvicorn

    print("Starting Alva Agent API...")
    print("Make sure your tool server is running on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8001)