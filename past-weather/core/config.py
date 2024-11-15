import os
import logging
from dotenv import load_dotenv
from fastapi.templating import Jinja2Templates
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

load_dotenv()
PREFIX = os.getenv("PREFIX", '').rstrip('/')
if not PREFIX.startswith('/'): # 반드시 '/'로 시작하도록 설정
    PREFIX = '/' + PREFIX

# 로깅 설정 (파일에 기록)
log_dir = "log"
os.makedirs(log_dir, exist_ok=True)  # log 디렉토리가 없으면 생성
templates = Jinja2Templates(directory="templates")

# TimedRotatingFileHandler 설정
current_date = datetime.now().strftime("%Y-%m-%d")
log_file_name = f"app-{current_date}.log"  # 로그 파일 이름 생성
log_file_path = os.path.join(log_dir, log_file_name)

handler = TimedRotatingFileHandler(log_file_path, when="midnight", interval=1, backupCount=7)
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(filename)s - line:%(lineno)d - %(message)s'))

logging.basicConfig(
    level=logging.WARN,
    handlers=[
        handler,
        logging.StreamHandler()  # 콘솔에도 로그 출력
    ]
)
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARN)
logging.getLogger('sqlalchemy.engine').propagate = True