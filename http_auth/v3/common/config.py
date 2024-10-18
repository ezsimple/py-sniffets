import os
from datetime import datetime
from dotenv import load_dotenv
import logging
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext

# .env를 환경변수에 로딩
load_dotenv()

# .env 내용을 공통변수로 저장
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

# 템플릿 경로 설정
templates = Jinja2Templates(directory="templates")

# 암호 라이브러리 지정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 로깅 설정 (파일에 기록)
log_dir = "log"
os.makedirs(log_dir, exist_ok=True)  # log 디렉토리가 없으면 생성
current_date = datetime.now().strftime("%Y-%m-%d")
log_file_name = f"app-{current_date}.log"  # 로그 파일 이름 생성

# 기본 로깅 설정
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(name)s - %(filename)s - line:%(lineno)d - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, log_file_name)),  # 로그를 log/app.log 파일에 기록
        logging.StreamHandler()  # 콘솔에도 로그 출력
    ]
)
logging.getLogger("starlette").setLevel(logging.WARNING)
logging.getLogger("fastapi").setLevel(logging.WARNING)
logging.getLogger("multipart.multipart").setLevel(logging.WARNING)  # form 데이트 로깅방지
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

