import os
import logging
import platform
from dotenv import load_dotenv
from fastapi.templating import Jinja2Templates

# 운영 체제에 따라 환경 변수 파일 로드
if platform.system() == 'Darwin':  # Mac OS
    load_dotenv('.env.mac')
else:  # Linux 및 기타 운영 체제는 기본 .env 파일 로드
    load_dotenv()

PREFIX = os.getenv("PREFIX", '').rstrip('/')
if not PREFIX.startswith('/'): # 반드시 '/'로 시작하도록 설정
    PREFIX = '/' + PREFIX

SESSION_KEY = os.getenv("SESSION_KEY")
if len(SESSION_KEY) == 0:
    raise ValueError("SESSION_KEY must be set in environment variables")

# 로깅 설정 (파일에 기록)
log_dir = "log"
os.makedirs(log_dir, exist_ok=True)  # log 디렉토리가 없으면 생성
templates = Jinja2Templates(directory="templates")

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(name)s - %(filename)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, "app.log")),  # 로그를 log/app.log 파일에 기록
        logging.StreamHandler()  # 콘솔에도 로그 출력
    ]
)

# 기본 로깅 설정
logging.getLogger("starlette").setLevel(logging.WARNING)
logging.getLogger("fastapi").setLevel(logging.WARNING)
logging.getLogger("multipart.multipart").setLevel(logging.WARNING)  # form 데이트 로깅방지
logger = logging.getLogger(__name__)