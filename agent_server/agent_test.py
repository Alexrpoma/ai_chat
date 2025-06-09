import asyncio
import configparser
import json  # ## NUEVO ## Importamos json para una bonita impresión
import re

import tiktoken
from agents import OpenAIChatCompletionsModel, ModelSettings, Runner, Agent, set_tracing_disabled
from agents.mcp import MCPServer, MCPServerStreamableHttp
from openai import AsyncOpenAI
from openai.types import Reasoning


# ## NUEVO ## - Función auxiliar para guardar el historial
def save_history_to_file(history, filename="chat_history.txt"):
    """Guarda el historial de chat en un archivo de texto de forma legible."""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write("=" * 20 + " INICIO DEL HISTORIAL DE CHAT " + "=" * 20 + "\n\n")
            # Usamos json.dumps para una visualización clara de la estructura
            # indent=2 hace que se vea bonito y legible
            f.write(json.dumps(history, indent=2, ensure_ascii=False))
            f.write("\n\n" + "=" * 20 + " FIN DEL HISTORIAL DE CHAT " + "=" * 20 + "\n")
    except Exception as e:
        print(f"⚠️  Error al guardar el historial: {e}")


def clean_assistant_response(response_text: str) -> str:
    pattern = r"<think>.*?</think>"
    cleaned_text = re.sub(pattern, "", response_text, flags=re.DOTALL)
    return cleaned_text.strip()


class AgentService:
    def __init__(self):
        config = configparser.ConfigParser()
        # Ojo: Para que funcione, el archivo config.ini debe existir
        # Si no existe, config.get puede fallar. Puedes añadir un try-except o asegurarte de que exista.
        config.read('config.ini')  # Asegúrate de que este archivo exista y se lea

        set_tracing_disabled(disabled=True)
        llm_url = config.get("LLM", "URL", fallback="http://localhost:11434/v1")
        api_key = config.get("LLM", "API_KEY", fallback="anything_for_testing")
        # self.__model = config.get("LLM", "MODEL", fallback="qwen2.5c:0.5b")
        self.__model = config.get("LLM", "MODEL", fallback="qwen3:0.6b")
        self.__client = AsyncOpenAI(base_url=llm_url, api_key=api_key)

        self.__instructions = f"""You are Alva, a friendly and highly capable AI agent with access to a comprehensive toolset. 
            PERSONALITY & BEHAVIOR:
            - Be conversational, helpful, and proactive
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

        self.MAX_CONTEXT_TOKENS = 4096  # Ajusta al límite de tu modelo
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        self.current_history_tokens = self.count_initial_tokens()

        save_history_to_file(self.__chat_history)

    def count_tokens_for_message(self, message: dict) -> int:
        """Calcula el número de tokens para un solo mensaje (aproximación)."""
        num_tokens = 4  # Sobrecarga por mensaje
        for key, value in message.items():
            num_tokens += len(self.tokenizer.encode(value))
        return num_tokens

    def count_initial_tokens(self) -> int:
        """Cuenta los tokens solo para el historial inicial (system prompt)."""
        return self.count_tokens_for_message(self.__chat_history[0])

    # ## NUEVO ## - Función de truncamiento MÁS PRECISA
    def truncate_history(self):
        """Trunca el historial si el conteo de tokens excede el máximo."""
        if self.current_history_tokens <= self.MAX_CONTEXT_TOKENS:
            return  # No hay nada que hacer

        print(
            f"Tokens actuales ({self.current_history_tokens}) exceden el límite ({self.MAX_CONTEXT_TOKENS}). Truncando...")

        # Bucle para eliminar mensajes antiguos hasta estar dentro del límite
        # Siempre dejamos el system_prompt (índice 0) y el último par user/assistant
        while self.current_history_tokens > self.MAX_CONTEXT_TOKENS and len(self.__chat_history) > 3:
            # Elimina el par de mensajes más antiguo (user y assistant) después del system prompt
            removed_user_msg = self.__chat_history.pop(1)
            removed_assistant_msg = self.__chat_history.pop(1)  # Ahora el assistant está en el índice 1

            # Restamos los tokens de los mensajes eliminados de nuestro contador global
            self.current_history_tokens -= self.count_tokens_for_message(removed_user_msg)
            self.current_history_tokens -= self.count_tokens_for_message(removed_assistant_msg)

            print(f"Par de mensajes eliminado. Tokens actuales: ~{self.current_history_tokens}")

    async def run(self, mcp_server: MCPServer):
        agent = Agent(
            name="Alva",
            model=OpenAIChatCompletionsModel(model=self.__model, openai_client=self.__client),
            mcp_servers=[mcp_server],
            model_settings=ModelSettings(tool_choice="required",
                                         temperature=0.1,
                                         top_p=1.0,
                                         extra_body={'enable_thinking': False})
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

                self.current_history_tokens += self.count_tokens_for_message(user_message)

                # 3. Truncamos ANTES de la llamada a la API para asegurar que no falle
                self.truncate_history()

                # ## NUEVO ## - Guardamos el historial justo ANTES de enviarlo al modelo
                # print("📝 Guardando historial actualizado en chat_history.txt...")
                save_history_to_file(self.__chat_history, "chat_history_before_llm.txt")

                result = await Runner.run(starting_agent=agent, input=self.__chat_history)

                # 5. ## LA MAGIA SUCEDE AQUÍ ##
                # Actualizamos el contador con los datos REALES de la API para el último turno
                if result and result.raw_responses:
                    turn_input_tokens = 0
                    turn_output_tokens = 0
                    for response in result.raw_responses:
                        if response.usage:
                            turn_input_tokens += response.usage.input_tokens
                            turn_output_tokens += response.usage.output_tokens

                    print(f"Uso real de la API en este turno: {turn_input_tokens} input, {turn_output_tokens} output.")

                    # Para una contabilidad perfecta, recalculamos todo el historial
                    # basado en los datos de la última llamada.
                    # El `turn_input_tokens` representa el costo de TODO el historial enviado.
                    self.current_history_tokens = turn_input_tokens

                if result and result.final_output:
                    assistant_response = result.final_output
                    cleaned_assistant_response = clean_assistant_response(assistant_response)
                    assistant_message = {"role": "assistant", "content": cleaned_assistant_response}
                    # print(f"Alva: {assistant_response}")
                    print(f"Alva: {cleaned_assistant_response}")
                    self.__chat_history.append(assistant_message)
                    if result and result.raw_responses and turn_output_tokens > 0:
                        self.current_history_tokens += turn_output_tokens
                    else:
                        # Fallback a estimación si la API no devuelve usage
                        self.current_history_tokens += self.count_tokens_for_message(assistant_message)

                    print(f"Tokens totales del historial para la próxima ronda: {self.current_history_tokens}")
                else:
                    print("Alva: I'm having trouble processing that request. Could you try rephrasing it?")

                # ## NUEVO ## - Guardamos el historial DESPUÉS de añadir la respuesta del asistente
                # print("📝 Guardando historial final de la ronda en chat_history.txt...")
                save_history_to_file(self.__chat_history, "chat_history_after_llm.txt")

                max_history_items = 30
                if len(self.__chat_history) > max_history_items:
                    self.__chat_history = [self.__chat_history[0]] + self.__chat_history[-(max_history_items - 1):]
                    print(f"Chat history truncated to {len(self.__chat_history)} items.")
                    # ## NUEVO ## - Opcional: Guardar el historial también después de truncar
                    save_history_to_file(self.__chat_history, "chat_history_truncated.txt")


            except KeyboardInterrupt:
                print("\nAlva: Goodbye! 👋")
                break
            except Exception as e:
                print(f"\n❌ An error occurred: {e}")
                print("Let's continue chatting...")
                continue

    # El resto del código no necesita cambios...
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