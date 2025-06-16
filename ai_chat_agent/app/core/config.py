import configparser


class Settings:
    def __init__(self, config_file: str = "config.ini"):
        config = configparser.ConfigParser()
        config.read(config_file)

        self.llm_url: str = config.get("LLM", "URL")
        self.llm_api_key: str = config.get("LLM", "API_KEY")
        self.llm_model: str = config.get("LLM", "MODEL")

        self.max_context_tokens: int = 2048 # TODO: Current value must be adjusted based on the model used

settings = Settings()