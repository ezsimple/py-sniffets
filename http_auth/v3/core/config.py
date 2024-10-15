import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PREFIX: str = os.getenv("PREFIX")
    JWT_SECRET: str = os.getenv("JWT_SECRET")
    JWT_EXPIRATION: int = int(os.getenv("JWT_EXPIRATION"))
    USERNAME: str = os.getenv("USERNAME")
    PASSWORD: str = os.getenv("PASSWORD")
    ROOT_DIR: str = os.getenv("ROOT_DIR")
    HOST: str = os.getenv("HOST")
    PORT: int = int(os.getenv("PORT"))

settings = Settings()

def print_host_port():
    print(settings.HOST, settings.PORT)