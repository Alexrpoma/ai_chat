import json
import re
from datetime import timedelta
from typing import List, Dict, Optional, Any

import tiktoken
from agents import OpenAIChatCompletionsModel, ModelSettings, Runner, Agent, set_tracing_disabled
from agents.mcp import MCPServerStreamableHttp
from openai import AsyncOpenAI

from ..core.config import settings
from ..models.context_models import ChatContext
from ..models.service_models import ProcessedChatResult


def clean_assistant_response(response_text: str) -> str:
    pattern = r"<think>.*?</think>"
    cleaned_text = re.sub(pattern, "", response_text, flags=re.DOTALL)
    return cleaned_text.strip()


class AgentService:
    def __init__(self):
        self.__client = AsyncOpenAI(base_url=settings.llm_url, api_key=settings.llm_api_key)
        self.__model = settings.llm_model

        self.__instructions = """You are Alva, a friendly and highly capable AI agent with access to a comprehensive toolset. 
            PERSONALITY & BEHAVIOR:
            - Be conversational, helpful, and proactive
            - For Mathematical operations, use the provided tools instead of manual calculations
            - Your primary goal is to use tools to assist the user. However, if a direct conversational response is more appropriate and no tool adds value, you may respond directly.
            - If a user asks something that could benefit from multiple tools, suggest or use them
            - If you encounter errors, explain them clearly and offer alternatives

            TOOL USAGE GUIDELINES:
            - Always use tools when they can help answer the user's question
            - For mathematical operations, prefer the specific tools over manual calculation
            - When users ask about capabilities, mention relevant tools
            Remember: You're not just answering questions, you're helping users accomplish tasks efficiently with your tools."""

        self.__base_history = [{"role": "system", "content": self.__instructions}]
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

        print("🤖 AgentService initialized successfully.")
        print(f"Model: {self.__model}, URL: {settings.llm_url}")

    def count_tokens_for_message(self, message: dict) -> int:
        num_tokens = 4
        for key, value in message.items():
            num_tokens += len(self.tokenizer.encode(str(value)))
        return num_tokens

    def count_total_tokens(self, messages: List[Dict]) -> int:
        return sum(self.count_tokens_for_message(msg) for msg in messages)

    def truncate_history(self, chat_history: List[Dict]) -> List[Dict]:
        total_tokens = self.count_total_tokens(chat_history)
        if total_tokens <= settings.max_context_tokens:
            return chat_history

        print(f"⚠️  Tokens ({total_tokens}) > Limit ({settings.max_context_tokens}). Truncating...")
        system_message = chat_history[0]
        conversation = chat_history[1:]
        while self.count_total_tokens([system_message] + conversation) > settings.max_context_tokens and len(
                conversation) > 1:
            conversation.pop(0)
            conversation.pop(0)

        final_history = [system_message] + conversation
        print(f"✅ History truncated. Final tokens: ~{self.count_total_tokens(final_history)}")
        return final_history

    async def process_chat(self, prompt: str, history: List[Dict], metadata: Optional[Dict[str, Any]] = None) -> str | ProcessedChatResult:
        current_chat_history = self.__base_history.copy()

        chat_context = ChatContext(**(metadata or {}))

        context_info = []
        if chat_context.partyId:
            context_info.append(f"Party ID: {chat_context.partyId}")
        if chat_context.sessionId:
            context_info.append(f"Session ID: {chat_context.sessionId}")
        if chat_context.serviceIdentifier:
            context_info.append(f"Service Identifier: {chat_context.serviceIdentifier}")

        if context_info:
            context_string = "; ".join(context_info)
            prompt += f", Context: {context_string}"

        print(f"Current prompt: {prompt}")

        current_chat_history.extend(history)
        current_chat_history.append({"role": "user", "content": prompt})

        current_chat_history = self.truncate_history(current_chat_history)

        set_tracing_disabled(disabled=True)

        final_response_content = ""
        transaction_id = None

        async with MCPServerStreamableHttp(
                name="Streamable HTTP Python Server",
                params={
                    "url": "http://localhost:8000/mcp",
                    "timeout": timedelta(seconds=6)
                },
        ) as server:
            agent = Agent(
                name="Alva",
                model=OpenAIChatCompletionsModel(model=self.__model, openai_client=self.__client),
                mcp_servers=[server],
                model_settings=ModelSettings(tool_choice="auto", temperature=0.1, top_p=0.95),
                tool_use_behavior="stop_on_first_tool",
            )
            result = await Runner.run(starting_agent=agent, input=current_chat_history)

        if result and result.final_output:
            output_string = result.final_output
            try:
                output_data = json.loads(output_string)
                if isinstance(output_data, dict):
                    final_response_content = output_data.get("html", str(output_data))
                    transaction_id = output_data.get("transactionId")
                else:
                    final_response_content = clean_assistant_response(str(output_data))

            except (json.JSONDecodeError, TypeError):
                final_response_content = clean_assistant_response(output_string)

        if not final_response_content:
            return "Sorry, I had trouble processing your request."

        return ProcessedChatResult(
            content=final_response_content,
            transactionId=transaction_id
        )