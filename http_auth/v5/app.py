import os
import re
import magic
import time
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, APIRouter, status, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pathlib import Path
from urllib.parse import unquote, quote
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware import Middleware
from starlette.responses import Response, RedirectResponse, FileResponse, HTMLResponse
from core.config import settings
from core.model import User, LoginRequiredMiddleware, CustomTemplateResponse, RedirectGetResponse
import aioredis
import jwt
from keycloak import KeycloakOpenID
from fastapi.security import OAuth2PasswordBearer
import logging
import json
from keycloak.exceptions import KeycloakPostError

logging.basicConfig(level=logging.DEBUG)  # DEBUG 레벨로 로그 출력 설정
logger = logging.getLogger("keycloak")  # Keycloak 관련 로그를 위한 로거 생성

# Redis 클라이언트 초기화
redis_client = aioredis.from_url(settings.SESSION_SERVER)

class LoginRequiredMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 쿠키에서 access_token 가져오기
        access_token = request.cookies.get("access_token")

        # 특정경로 인증 생략
        if request.url.path.startswith(f"{settings.PREFIX}/token") \
                or request.url.path.startswith(f"{settings.PREFIX}/auth/callback") \
                or request.url.path.startswith("/static/"):
            response = await call_next(request)
            return response

        # 로그인 페이지 접근시
        if request.url.path.startswith(f"{settings.PREFIX}/login"):
            if access_token:
                try:
                    payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=["HS256"])
                    request.state.user = User(username=payload["sub"])  # 사용자 정보 설정
                except jwt.PyJWTError:
                    pass

            response = await call_next(request)
            return response

        # 로그인 페이지가 아닌 다른 경로 접근시
        if not access_token:
            return RedirectGetResponse(url=f"{settings.PREFIX}/login?_={int(time.time())}")

        try:
            payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=["HS256"])
            username=payload["sub"]
            request.state.user = User(username=username)  # 사용자 정보 설정
            # 세션 연장
            # refresh_token으로 변경되어야 해서, 아래 주석처리
            # await redis_client.expire(username, settings.SESSION_TIMEOUT)
        except jwt.PyJWTError:
            return RedirectGetResponse(url=f"{settings.PREFIX}/login?_={int(time.time())}")

        keycloak_response = await redis_client.get(username)
        if keycloak_response:
            # 바이트 문자열을 UTF-8 문자열로 디코딩
            keycloak_response = keycloak_response.decode('utf-8')
            # json 은  쌍따옴표(")를 사용해야 json.loads를 사용할 수 있음.
            keycloak_response = keycloak_response.replace("'", '"')
            keycloak_response = json.loads(keycloak_response)
            refresh_token = keycloak_response.get('refresh_token')
            try:
                new_token = keycloak_openid.refresh_token(refresh_token)
                new_token = str(new_token).replace("'", '"')
                # 세션 연장
                await redis_client.set(username, str(new_token), ex=settings.SESSION_TIMEOUT)
            except KeycloakPostError as e:
                logger.error(f"Keycloak refresh_token error: {e}")
                return RedirectGetResponse(url=f"{settings.PREFIX}/logout")

        response = await call_next(request)
        return response


# 순서중요합니다. SessionMiddleWare가 항상 먼저 와야함.
middleware = [
    Middleware(SessionMiddleware, secret_key=settings.SECRET_KEY),
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
app.mount(settings.STATIC_URL, StaticFiles(directory="static"), name="static")
router = APIRouter(prefix=settings.PREFIX)

keycloak_openid = KeycloakOpenID(server_url=settings.KEYCLOAK_SERVER_URL,
                                 client_id=settings.KEYCLOAK_CLIENT_ID,
                                 client_secret_key=settings.KEYCLOAK_CLIENT_SECRET,
                                 realm_name=settings.KEYCLOAK_REALM)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.PREFIX}/token")

# HTTPException 처리기
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # 예외 로그 기록
    logger.error(f"HTTPException occurred: {exc.detail}, Status code: {exc.status_code}, Path: {request.url.path}")
    return RedirectGetResponse(url=f"{settings.PREFIX}/login?_={int(time.time())}")

# ValueError 처리기
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    # 예외 로그 기록
    logger.error(f"ValueError occurred: {exc}, Path: {request.url.path}")
    return RedirectGetResponse(url=f"{settings.PREFIX}/login?_={int(time.time())}") # 추후 에러페이지로

@router.get("/login")
async def login_view(request: Request, response: Response):
    if not hasattr(request.state, 'user') or request.state.user is None:
        return CustomTemplateResponse("login.html", {"request": request})
    return RedirectGetResponse(url=f"{settings.PREFIX}/dl")

@app.get(f"{settings.PREFIX}/protected")
async def protected_route(token: str = Depends(oauth2_scheme)):
    try:
        userinfo = keycloak_openid.userinfo(token)
        return {"message": "Protected route", "user": userinfo}
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

async def build_access_token(username: str):
    '''
    LoginMiddleWare에서 인증여부 확인을 위해 사용
    Build Access Token Data
    '''
    token_data = {
        "sub": username,
        "exp": datetime.utcnow() + timedelta(seconds=settings.SESSION_TIMEOUT)
    }
    access_token = jwt.encode(token_data, settings.SECRET_KEY, algorithm="HS256")
    return access_token

@app.post(f"{settings.PREFIX}/token", response_class=JSONResponse)
async def login(request: Request, response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    # logger.debug(f"Username: {form_data.username}, Password: {form_data.password}")
    try:
        keycloak_response = keycloak_openid.token(form_data.username, form_data.password)
    except Exception as e:
        logging.debug(str(e))
        return JSONResponse(content={"message": "Incorrect username or password"}, status_code=status.HTTP_401_UNAUTHORIZED)

    keycloak_response = str(keycloak_response).replace("'", '"')
    keycloak_response = json.loads(keycloak_response)
    await redis_client.set(form_data.username, str(keycloak_response), ex=settings.SESSION_TIMEOUT)
    access_token = await build_access_token(form_data.username)

    '''
    JWT를 쿠키에 저장
    HTTPOnly 속성: 쿠키에 httponly 속성을 설정하면
    JavaScript에서 접근할 수 없기 때문에 XSS(교차 사이트 스크립팅) 공격으로부터
    보호할 수 있습니다.

    모바일 브라우저에서 쿠키를 설정할 때,
    SameSite=None 및 Secure 속성을 설정하여 모바일 앱에서 쿠키를 수용할 수 있도록 합니다.
    '''
    response.set_cookie("access_token", access_token, httponly=True, max_age=settings.SESSION_TIMEOUT, samesite='None', secure=True)

    return keycloak_response

@router.api_route("/logout", methods=["GET", "POST"], response_class=RedirectResponse)
async def logout(request: Request):
    response = RedirectGetResponse(url=f"{settings.PREFIX}/login?_={int(time.time())}")
    access_token = request.cookies.get("access_token")
    try:
        payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=["HS256"])
        username = payload["sub"]
    except jwt.PyJWTError:
        return RedirectGetResponse(url=f"{settings.PREFIX}/login?_={int(time.time())}")

    if username:
        keycloak_response = await redis_client.get(username)
        if keycloak_response:
            # 바이트 문자열을 UTF-8 문자열로 디코딩
            keycloak_response = keycloak_response.decode('utf-8')
            # json 은  쌍따옴표(")를 사용해야 json.loads를 사용할 수 있음.
            keycloak_response = keycloak_response.replace("'", '"')
            keycloak_response = json.loads(keycloak_response)
            refresh_token = keycloak_response.get('refresh_token')
            keycloak_openid.logout(refresh_token)
            await redis_client.delete(username)

    response.delete_cookie("access_token")  # 쿠키 삭제

    # 캐시 방지 헤더 추가 (뒤로가기 방지)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'

    return response

@router.get("/", response_class=RedirectResponse)
async def redirect_to_dl(request: Request):
    if request.state.user:
        return RedirectGetResponse(url=f"{settings.PREFIX}/dl/")
    return RedirectGetResponse(url=f"{settings.PREFIX}/login?_={int(time.time())}") 

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
    # logger.debug(f'has_parent={has_parent}, remaining_path={remaining_path}, full_path={full_path}')

    # 파일이 디렉토리인지 여부 확인
    file_info = [(file.lstrip('/'), os.path.isdir(os.path.join(directory_path, file))) for file in filtered_files]

    # is_dir가 True인 항목과 False인 항목으로 분리
    directories = [(file, is_dir) for file, is_dir in file_info if is_dir]
    files = [(file, is_dir) for file, is_dir in file_info if not is_dir]

    # 두 목록을 합치고, 알파벳 순으로 정렬
    file_info = sorted(directories) + sorted(files)

    # 현재 경로 설정
    current_path = path.lstrip('/').rstrip('/')

    return CustomTemplateResponse("files.html", {
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
