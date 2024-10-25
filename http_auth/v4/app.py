import os
import re
import magic
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, APIRouter, Form, status, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pathlib import Path
from urllib.parse import unquote, quote
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware import Middleware
from starlette.responses import RedirectResponse, FileResponse, HTMLResponse
from core.config import PREFIX, SESSION_SERVER, SESSION_TIMEOUT, SECRET_KEY, logger
from core.model import User, Token, LoginForm, LoginRequiredMiddleware, CustomTemplateResponse, RedirectGetResponse
from passlib.context import CryptContext
import aioredis
import uuid
import jwt

# Redis 클라이언트 초기화
redis_client = aioredis.from_url(SESSION_SERVER)

class LoginRequiredMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):

        if request.url.path.startswith(f"{PREFIX}/login") \
                or request.url.path.startswith(f"{PREFIX}/token") \
                or request.url.path.startswith("/static/"):
            response = await call_next(request)
            return response

        # 쿠키에서 session_id 가져오기
        is_logined = False
        session_id = request.cookies.get("session_id")
        if session_id and await redis_client.exists(f"session:{session_id}"):
            try:
                access_token = request.session["access_token"]

                # 질문1 : 이게  session_id, access_token 을 refresh 해주는 코드가 맞나???
                await redis_client.expire(f"session:{session_id}", SESSION_TIMEOUT)
                await redis_client.expire(access_token, SESSION_TIMEOUT)  # 세션 연장

                # 이 코드는 필요가 없어 보임
                # payload = jwt.decode(access_token, SECRET_KEY, algorithms=["HS256"])
                # username = payload.get("sub")
                # request.state.user = User(username=username)    

                is_logined = True

            except jwt.PyJWTError:
                return RedirectGetResponse(url=f"{PREFIX}/login")

        if not is_logined:
            return RedirectGetResponse(url=f"{PREFIX}/login")

        response = await call_next(request)
        return response

# 순서중요합니다. SessionMiddleWare가 항상 먼저 와야함.
middleware = [
    Middleware(SessionMiddleware, secret_key=SECRET_KEY),
    Middleware(LoginRequiredMiddleware),
    Middleware(
      CORSMiddleware,
      allow_origins=["*"],  # 모든 도메인 허용, 필요에 따라 수정
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
    )
]

app = FastAPI(middleware=middleware)
app.mount("/static", StaticFiles(directory="static"), name="static")
router = APIRouter(prefix=PREFIX)  

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{PREFIX}/token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)

# def get_password_hash(password):
#     return pwd_context.hash(password)

def check_auth(form: LoginForm):
    correct_username = os.getenv("USERNAME")
    correct_password = os.getenv("PASSWORD")
    if form.username == correct_username and form.password == correct_password:
        return True
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

# def check_oauth2(form: LoginForm):
#     correct_username = os.getenv("USERNAME")
#     correct_password = get_password_hash(os.getenv("PASSWORD"))
#     if form.username == correct_username and form.password == correct_password:
#         return True
#     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

# HTTPException 처리기
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # 예외 로그 기록
    logger.error(f"HTTPException occurred: {exc.detail}, Status code: {exc.status_code}, Path: {request.url.path}")
    return RedirectGetResponse(url=f"{PREFIX}/login")

# ValueError 처리기
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    # 예외 로그 기록
    logger.error(f"ValueError occurred: {exc}, Path: {request.url.path}")
    return RedirectGetResponse(url=f"{PREFIX}/login") # 추후 에러페이지로

async def build_access_token(username: str):
    '''
    Build Access Token Data
    '''
    token_data = {
        "sub": username,
        "exp": datetime.utcnow() + timedelta(seconds=SESSION_TIMEOUT)
    }
    access_token = jwt.encode(token_data, SECRET_KEY, algorithm="HS256")
    return access_token

async def refresh_access_token(username: str, access_token: str):
    '''
    Refresh Redis Access Token
    '''
    await redis_client.set(access_token, username, ex=SESSION_TIMEOUT)

@app.post(f"{PREFIX}/token", response_model=Token)
async def login(request: Request, response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    form = LoginForm(username=form_data.username, password=form_data.password)
    check_auth(form)

    token_data = {
        "sub": form.username,
        "exp": datetime.utcnow() + timedelta(seconds=SESSION_TIMEOUT)
    }
    access_token = jwt.encode(token_data, SECRET_KEY, algorithm="HS256")
    await redis_client.set(access_token, form.username, ex=SESSION_TIMEOUT)

    session_id = str(uuid.uuid4())  # 새로운 세션 ID 생성
    await redis_client.set(f"session:{session_id}", form.username, ex=SESSION_TIMEOUT)  # 1분 타임아웃 설정
    response.set_cookie("session_id", session_id, httponly=True, max_age=SESSION_TIMEOUT) 
    request.state.user = User(username=form.username)
    request.session["access_token"] = access_token 

    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=User)
async def read_users_me(request: Request):
    return request.state.user

@app.post("/logout")
async def logout(request: Request):
    token = request.cookies.get("access_token")
    if token:
        await redis_client.delete(token)
    return {"msg": "Successfully logged out"}

@router.get("/login")
async def login_view(request: Request):
    # Redis에서 로그인 상태 확인
    session_id = request.cookies.get("session_id")
    if session_id:
        username = await redis_client.get(f"session:{session_id}")
        if username:
            return RedirectGetResponse(url=f"{PREFIX}/dl")

    return CustomTemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    form = LoginForm(username=username, password=password)
    check_auth(form)

    session_id = str(uuid.uuid4())  # 새로운 세션 ID 생성
    await redis_client.set(f"session:{session_id}", form.username, ex=SESSION_TIMEOUT)  # 1분 타임아웃 설정
    response = RedirectGetResponse(url=f"{PREFIX}/dl/")
    response.set_cookie("session_id", session_id, httponly=True, max_age=SESSION_TIMEOUT)  # 세션 ID를 쿠키에 저장

    return response

@router.api_route("/logout", methods=["GET", "POST"], response_class=RedirectResponse)
async def logout(request: Request):
    session_id = request.cookies.get("session_id")
    if session_id:
        await redis_client.delete(f"session:{session_id}")
    response = RedirectGetResponse(url=f"{PREFIX}/login")
    response.delete_cookie("session_id")  # 쿠키 삭제
    return response

@router.get("/", response_class=RedirectResponse)
async def redirect_to_dl(request: Request):
    session_id = request.cookies.get("session_id")
    if session_id:
        return RedirectGetResponse(url=f"{PREFIX}/dl/")
    return RedirectGetResponse(url=f"{PREFIX}/login")

@router.get("/dl/{path:path}", response_class=HTMLResponse)
async def list_files(request: Request, path: str = ''):
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

def guess_display_inline(file_path: str, mime_type: str) -> bool:
    if len(mime_type) == 0:
        return False

    # MIME 타입이 inline으로 열 수 있는지 확인 (추가적인 라이브러리 필요 없음)
    return mime_type.startswith('image/') or \
           mime_type.startswith('text/') or \
           mime_type in ['application/pdf', 'application/xhtml+xml']

@router.get("/download/{path:path}", response_class=FileResponse)
async def download_file(request: Request, path: str):
    path = unquote(path)  # URL 인코딩된 문자열을 디코딩
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
    mime = magic.Magic(mime=True)
    mime_type = mime.from_file(file_path)  # 파일의 MIME 타입 확인
    if mime_type:
        print(mime_type)

    # 디버깅 정보 로그
    logger.debug(f"media_type={mime_type or 'application/octet-stream'}, file_path={file_path}, filename={filename}, extension={extension}")

    # Content-Disposition 설정
    disposition = 'inline' if guess_display_inline(file_path, mime_type) else 'attachment'

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
