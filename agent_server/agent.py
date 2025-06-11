import asyncio
import configparser
import json
import re

import tiktoken
from agents import OpenAIChatCompletionsModel, ModelSettings, Runner, Agent, set_tracing_disabled, RunHooks
from agents.mcp import MCPServer, MCPServerStreamableHttp
from openai import AsyncOpenAI

import logging
logging.basicConfig(level=logging.DEBUG)


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

class AgentService:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        llm_url = config.get("LLM", "URL")
        api_key = config.get("LLM", "API_KEY")
        self.__model = config.get("LLM", "MODEL")
        self.__client = AsyncOpenAI(base_url=llm_url, api_key=api_key)

        self.__instructions = f"""You are Alva, a friendly and highly capable AI agent with access to a comprehensive toolset. 
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
        self.__chat_history = [
            {"role": "system", "content": self.__instructions}
        ]

        self.MAX_CONTEXT_TOKENS = 2048
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        self.current_context_tokens = self.count_initial_tokens()

        self.output_context_tokens = 0

        save_history_to_file(self.__chat_history)

    def count_tokens_for_message(self, message: dict) -> int:
        num_tokens = 4  # Overhead per message
        for key, value in message.items():
            num_tokens += len(self.tokenizer.encode(value))
        return num_tokens

    def count_initial_tokens(self) -> int:
        """Counts tokens only for the initial history (system prompt)."""
        return self.count_tokens_for_message(self.__chat_history[0])

    def truncate_history(self):
        """Truncates the chat history if the total token count exceeds the maximum allowed."""
        if self.current_context_tokens <= self.MAX_CONTEXT_TOKENS:
            return

        print(f"Current tokens ({self.current_context_tokens}) exceed the limit ({self.MAX_CONTEXT_TOKENS}). Truncating...")

        save_history_to_file(self.__chat_history, "chat_history_before_llm.txt")

        while self.current_context_tokens > self.MAX_CONTEXT_TOKENS and len(self.__chat_history) > 3:
            # Delete the oldest message pair (user and assistant) after the system prompt
            removed_user_msg = self.__chat_history.pop(1)
            removed_assistant_msg = self.__chat_history.pop(1)  # Now the assistant is at index 1

            # Subtracting the tokens of deleted messages from the global counter
            self.current_context_tokens -= self.count_tokens_for_message(removed_user_msg)
            self.current_context_tokens -= self.count_tokens_for_message(removed_assistant_msg)
            print(f"Pair of messages deleted. Current context tokens: ~{self.current_context_tokens}")

        save_history_to_file(self.__chat_history, "chat_history_truncated.txt")

    async def run(self, mcp_server: MCPServer):
        set_tracing_disabled(disabled=True)

        agent = Agent(
            name="Alva",
            model=OpenAIChatCompletionsModel(model=self.__model, openai_client=self.__client),
            mcp_servers=[mcp_server],
            model_settings=ModelSettings(tool_choice="auto", temperature=0.1, top_p=0.95)
        )

        while True:
            try:
                user_input = await asyncio.to_thread(input, "You: ")

                if user_input.lower() in ["exit", "quit"]:
                    print("Alva: Goodbye! 👋")
                    break

                if not user_input.strip():
                    continue

                user_message = {"role": "user", "content": user_input}

                self.__chat_history.append(user_message)
                self.current_context_tokens += self.count_tokens_for_message(user_message)

                self.truncate_history() # Ensure history is within token limits

                save_history_to_file(self.__chat_history, "current_chat_history_llm.txt")

                result = await Runner.run(starting_agent=agent, input=self.__chat_history)

                if result and result.raw_responses:
                    self.current_context_tokens = result.raw_responses[0].usage.input_tokens

                    # Total tokens processed
                    turn_input_tokens = 0
                    turn_output_tokens = 0
                    for response in result.raw_responses:
                        if response.usage:
                            turn_input_tokens += response.usage.input_tokens
                            turn_output_tokens += response.usage.output_tokens
                    print(f"API: Total tokens usage this turn: {turn_input_tokens} input, {turn_output_tokens} output.")

                if result and result.final_output:
                    assistant_response = result.final_output
                    cleaned_assistant_response = clean_assistant_response(assistant_response)
                    assistant_message = {"role": "assistant", "content": cleaned_assistant_response}
                    # print(f"Alva: {assistant_response}")
                    print(f"Alva: {cleaned_assistant_response}")
                    self.__chat_history.append(assistant_message)
                    self.current_context_tokens += self.count_tokens_for_message(assistant_message)

                    print(f"Total history tokens for the next round: {self.current_context_tokens}")
                else:
                    print("Alva: I'm having trouble processing that request. Could you try rephrasing it?")

                save_history_to_file(self.__chat_history, "chat_history_before_llm.txt")

            except KeyboardInterrupt:
                print("\nAlva: Goodbye! 👋")
                break
            except Exception as e:
                print(f"\n❌ An error occurred: {e}")
                print("Let's continue chatting...")
                continue

    async def streamable_http(self):
        async with MCPServerStreamableHttp(
            name="Streamable HTTP Python Server",
            params={
                "url": "http://localhost:8000/mcp",
            },
        ) as server:
            print("Initializing Alva agent")
            print(f"Using model: {self.__model} via {self.__client.base_url}")
            await self.run(server)

if __name__ == "__main__":
    asyncio.run(AgentService().streamable_http())