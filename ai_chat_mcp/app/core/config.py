import configparser


class Settings:
    def __init__(self, config_file: str = "config.ini"):
        config = configparser.ConfigParser()
        config.read(config_file)

        self.bills_api_url: str = config.get("EXTERNAL_SERVICES", "BILLS_API_URL")

settings = Settings()