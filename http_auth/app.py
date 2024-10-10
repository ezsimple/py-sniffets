from fastapi import FastAPI, Depends, HTTPException, APIRouter, Form, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
# from fastapi.security import HTTPBasic, HTTPBasicCredentials
import os
import re
from dotenv import load_dotenv
from pathlib import Path
import mimetypes
import logging
from urllib.parse import unquote, quote
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse, FileResponse, HTMLResponse
from starlette.requests import Request
import platform
from datetime import datetime
import pdb

# 운영 체제에 따라 환경 변수 파일 로드
if platform.system() == 'Darwin':  # Mac OS
    load_dotenv('.env.mac')
else:  # Linux 및 기타 운영 체제는 기본 .env 파일 로드
    load_dotenv()

app = FastAPI()

# 세션 미들웨어 추가 (비밀키 설정 필요)
session_key = os.getenv("SESSION_KEY")
if not session_key:
    raise ValueError("SESSION_KEY must be set in environment variables")
app.add_middleware(SessionMiddleware, secret_key=session_key)

# get_session, set_session 함수들은 FastAPI 애플리케이션의 엔드포인트로 정의되어 있습니다.
@app.get("/set_session")
async def set_session(request: Request, username: str):
    # 세션에 값 저장
    request.session["username"] = username
    return {"message": "세션에 username 저장 완료"}

@app.get("/get_session")
async def get_session(request: Request):
    username = request.session.get("username")
    if username:
        return {"username": username}
    return {"message": "세션에 username이 없습니다."}

# 로그 디렉토리 생성
log_dir = "log"
os.makedirs(log_dir, exist_ok=True)  # log 디렉토리가 없으면 생성

# 로깅 설정 (파일에 기록)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, "app.log")),  # 로그를 log/app.log 파일에 기록
        logging.StreamHandler()  # 콘솔에도 로그 출력
    ]
)
logger = logging.getLogger(__name__)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인 허용, 필요에 따라 수정
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 모든 요청에 대해 타임스탬프를 전달하는 라우터
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# security = HTTPBasic()
router = APIRouter(prefix="/v1")  # /v1 경로를 prefix로 설정

# Pydantic 모델 정의
class LoginForm(BaseModel):
    username: str
    password: str

class RedirectGetResponse(RedirectResponse):
    def __init__(self, url: str, **kwargs):
        # status_code를 303으로 설정
        # 302: 일시적 리다이렉션, 원래 HTTP 메서드를 유지.
        # 303: 리소스가 다른 URI에 있으며, GET 메서드를 사용하여 요청해야 함.
        # 307 Temporary Redirect: 요청한 리소스가 일시적으로 다른 URI로 이동했으며, 클라이언트는 원래의 HTTP 메서드를 유지해야 합니다. 
        super().__init__(url=url, status_code=status.HTTP_303_SEE_OTHER, **kwargs)

class LoginRequiredMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 세션에서 로그인 상태 확인
        is_logined = "username" in request.session
        
        # 로그인하지 않은 경우 리다이렉트
        if not is_logined:
            return RedirectGetResponse(url="/v1/login")

        # 다음 미들웨어 또는 요청 처리기로 넘어감
        response = await call_next(request)
        return response

# 로그인 미들웨어 등록
app.add_middleware(LoginRequiredMiddleware)

class CustomTemplateResponse(HTMLResponse):
    def __init__(self, template_name: str, context: dict):
        # 현재 타임스탬프를 context에 추가
        context["timestamp"] = datetime.now().timestamp() 

        # 로그인 상태 확인
        is_logined = "username" in context.get("request").session
        context["is_logined"] = is_logined 

        super().__init__(content=templates.get_template(template_name).render(context))

def check_auth(form: LoginForm):
    correct_username = os.getenv("USERNAME")
    correct_password = os.getenv("PASSWORD")
    if form.username == correct_username and form.password == correct_password:
        return True
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

# HTTPException 처리기
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # 예외 로그 기록
    logger.error(f"HTTPException occurred: {exc.detail}, Status code: {exc.status_code}, Path: {request.url.path}")
    return RedirectGetResponse(url="/v1/login")

# ValueError 처리기
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    # 예외 로그 기록
    logger.error(f"ValueError occurred: {exc}, Path: {request.url.path}")
    return RedirectGetResponse(url="/v1/login") # 추후 에러페이지로

@router.get("/login")
async def get_login(request: Request):

    # LoginRequiredMiddleware 에서 처리
    # is_logined = 'username' in request.session
    # if is_logined:
    #     return RedirectGetResponse(url="/v1/dl")

    return CustomTemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    # 폼객체로 변환
    form = LoginForm(username=username, password=password)
    check_auth(form)

    # 세션에 사용자 정보 저장
    request.session['username'] = form.username

    # 303 응답 코드로 GET 요청으로 리다이렉트
    # (주의) status_code=307을 사용하면 POST 요청으로 리다이렉트됨
    return RedirectGetResponse(url="/v1/dl/")

@router.api_route("/logout", methods=["GET", "POST"], response_class=RedirectResponse)
async def logout(request: Request):
    request.session.pop('username', None)
    return RedirectGetResponse(url="/v1")

@router.get("/", response_class=RedirectResponse)
async def redirect_to_dl():
    return RedirectGetResponse(url="/v1/dl/")

@router.get("/dl/{path:path}", response_class=HTMLResponse)
async def list_files(request: Request, path: str = ''):

    # 로그인 상태 체크
    # LoginRequiredMiddleware 에서 처리
    # is_logined = 'username' in request.session
    # if not is_logined:
    #     return RedirectGetResponse(url="/v1/login")

    root_dir = os.getenv("ROOT_DIR")
    directory_path = os.path.join(root_dir, path.lstrip("/")).rstrip("/")  # 선행 슬래시 제거 및 마지막 슬래시 제거

    if not os.path.isdir(directory_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Directory not found")

    files = os.listdir(directory_path)
    ignore_file_path = os.path.join(directory_path, '.ignorefiles')
    ignored_patterns = []

    if os.path.isfile(ignore_file_path):
        with open(ignore_file_path, 'r') as f:
            ignored_patterns = [line.strip() for line in f if line.strip()]

    regex_patterns = [re.escape(pattern).replace(r'\*', '.*') for pattern in ignored_patterns]
    filtered_files = [file for file in files if not any(re.match(pattern, file) for pattern in regex_patterns)]

    readme_content = get_readme_content(directory_path)

    # 상위 디렉토리 경로 계산
    parent_path = ""  # path가 비어있다면 parent_path도 비워둠
    if path:  # path가 비어있지 않을 때
        parent_path = os.path.dirname(path).rstrip("/")  # 마지막 슬래시 제거

    # 현재 요청한 전체 경로
    full_path = path  # 요청한 전체 경로 (예: "ROOT_DIR/서브디렉토리/파일")

    # ROOT_DIR을 제거
    remaining_path = full_path.replace(root_dir, "", 1).lstrip("/")  # ROOT_DIR 만큼 삭제하고 선행 슬래시 제거

    # has_parent 결정
    has_parent = bool(remaining_path)  # 남은 스트링이 있으면 True
    logger.debug(f'has_parent={has_parent}, remaining_path={remaining_path}, full_path={full_path}')

    # 파일이 디렉토리인지 여부 확인
    file_info = [(file.lstrip('/'), os.path.isdir(os.path.join(directory_path, file))) for file in filtered_files]

    # is_dir가 True인 항목과 False인 항목으로 분리
    directories = [(file, is_dir) for file, is_dir in file_info if is_dir]
    files = [(file, is_dir) for file, is_dir in file_info if not is_dir]

    # 두 목록을 합치고, 알파벳 순으로 정렬
    file_info = sorted(directories) + sorted(files)

    # 현재 경로 설정
    current_path = path.lstrip('/').rstrip('/')

    return CustomTemplateResponse("index.html", {
        "request": request,
        "file_info": file_info,
        "readme_content": readme_content,
        "current_path": path.lstrip('/').rstrip('/'),
        "parent_path": parent_path,
        "is_root": (path == ''),  # 최상위 경로인지 여부
        "has_parent": has_parent,  # 상위 디렉토리가 있는지 여부
    })

@router.get("/download/{path:path}", response_class=FileResponse)
async def download_file(request: Request, path: str):

    # pdb.set_trace()
    # session_id = request.session.get("session_id")
    # logger.debug(f"Session ID from request.session.get(session_id): {session_id}")
    # 세션ID를 알수가 없네.. 뭐지????
    # request.session.get("session_id") 이거 왜 안되지???? 값이 None으로 나와

    path = unquote(path)  # URL 인코딩된 문자열을 디코딩
    logger.debug(f"path=/v1/download/{path}")

    root_dir = os.getenv("ROOT_DIR")

    # 직접 경로 생성
    file_path = os.path.join(root_dir, path.lstrip('/'))  # 선행 슬래시 제거
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    # file 객체 생성
    file = Path(file_path)

    # 파일 이름 추출
    filename = file.name

    # 파일 확장자 추출
    extension = file.suffix

    # MIME 타입 자동 설정
    mime_type, _ = mimetypes.guess_type(file_path)

    # 디버깅 정보 로그
    logger.debug(f"media_type={mime_type or 'application/octet-stream'}, file_path={file_path}, filename={filename}, extension={extension}")

    # Content-Disposition 설정
    disposition = 'attachment'  # default : 다운로드할 파일
    if extension in ['.pdf', '.txt', '.jpg', '.jpeg', '.png', '.gif']:  # 직접 열 수 있는 파일 형식
        disposition = 'inline'

    # 파일 이름을 UTF-8로 인코딩
    encoded_filename = quote(filename.encode('utf-8'))
    response = FileResponse(file_path, media_type=mime_type or 'application/octet-stream')
    response.headers["Content-Disposition"] = f'{disposition}; filename="{encoded_filename}"'

    return response

def get_readme_content(path):
    readme_path = os.path.join(path, '.README')
    if os.path.isfile(readme_path):
        with open(readme_path, 'r') as f:
            content = f.readlines()
        return '<br>'.join(line.strip() for line in content if not line.startswith('#'))
    return ""

app.include_router(router)  # 라우터 등록

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST")
    port = int(os.getenv("PORT"))
    uvicorn.run(app, host=host, port=port)
