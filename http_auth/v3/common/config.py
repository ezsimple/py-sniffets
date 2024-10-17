import os
from dotenv import load_dotenv
import logging
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext

load_dotenv()

# 로깅 설정 (파일에 기록)
log_dir = "log"
os.makedirs(log_dir, exist_ok=True)  # log 디렉토리가 없으면 생성
templates = Jinja2Templates(directory="templates")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 기본 로깅 설정
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(name)s - %(filename)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, "app.log")),  # 로그를 log/app.log 파일에 기록
        logging.StreamHandler()  # 콘솔에도 로그 출력
    ]
)
logging.getLogger("starlette").setLevel(logging.WARNING)
logging.getLogger("fastapi").setLevel(logging.WARNING)
logging.getLogger("multipart.multipart").setLevel(logging.WARNING)  # form 데이트 로깅방지
logger = logging.getLogger(__name__)

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