import os
from dotenv import load_dotenv
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext

load_dotenv()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Settings:
    PREFIX: str = os.getenv("PREFIX")
    JWT_SECRET: str = os.getenv("JWT_SECRET")
    JWT_EXPIRATION: int = int(os.getenv("JWT_EXPIRATION"))
    USERNAME: str = os.getenv("USERNAME")
    PASSWORD: str = pwd_context.hash(os.getenv("PASSWORD"))
    ROOT_DIR: str = os.getenv("ROOT_DIR")
    HOST: str = os.getenv("HOST")
    PORT: int = int(os.getenv("PORT"))

settings = Settings()

# 로깅 설정 (파일에 기록)
log_dir = "log"
os.makedirs(log_dir, exist_ok=True)  # log 디렉토리가 없으면 생성
templates = Jinja2Templates(directory="templates")