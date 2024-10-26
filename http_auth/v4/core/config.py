import os
import logging
import platform
from dotenv import load_dotenv
from fastapi.templating import Jinja2Templates
from datetime import datetime

# 운영 체제에 따라 환경 변수 파일 로드
if platform.system() == 'Darwin':  # Mac OS
    load_dotenv('.env.mac')
else:  # Linux 및 기타 운영 체제는 기본 .env 파일 로드
    load_dotenv()

PREFIX = os.getenv("PREFIX", '').rstrip('/')
if not PREFIX.startswith('/'): # 반드시 '/'로 시작하도록 설정
    PREFIX = '/' + PREFIX

SECRET_KEY = os.getenv("SECRET_KEY")
if len(SECRET_KEY) == 0:
    raise ValueError("SECRET_KEY must be set in environment variables")

SESSION_SERVER = os.getenv("SESSION_SERVER")
if len(SESSION_SERVER) == 0:
    raise ValueError("SESSION_SERVER must be set in environment variables")

SESSION_TIMEOUT = int(os.getenv("SESSION_TIMEOUT", 60))

# Google OAuth2 설정
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
GOOGLE_TOKEN_URI = os.getenv("GOOGLE_TOKEN_URI")
GOOGLE_AUTH_URI = os.getenv("GOOGLE_AUTH_URI")

# 로깅 설정 (파일에 기록)
log_dir = "log"
current_date = datetime.now().strftime("%Y-%m-%d")
log_file_name = f"app-{current_date}.log"  # 로그 파일 이름 생성

os.makedirs(log_dir, exist_ok=True)  # log 디렉토리가 없으면 생성
templates = Jinja2Templates(directory="templates")

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(name)s - %(filename)s - line:%(lineno)d - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, log_file_name)),  # 로그를 log/app.log 파일에 기록
        logging.StreamHandler()  # 콘솔에도 로그 출력
    ]
)

# 기본 로깅 설정
logging.getLogger("starlette").setLevel(logging.WARNING)
logging.getLogger("fastapi").setLevel(logging.WARNING)
logging.getLogger("multipart.multipart").setLevel(logging.WARNING)  # form 데이트 로깅방지
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)