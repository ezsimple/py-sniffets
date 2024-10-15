import os
import logging
import platform
from dotenv import load_dotenv
from fastapi.templating import Jinja2Templates
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta

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

# JWT 설정
SECRET_KEY = SESSION_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2PasswordBearer 정의
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{PREFIX}/login")

# JWT 생성 함수
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# JWT 검증 함수
def verify_token(token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except JWTError:
        raise credentials_exception