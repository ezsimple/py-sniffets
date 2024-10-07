from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import os
import re
from dotenv import load_dotenv
from pathlib import Path
import mimetypes
import logging
from urllib.parse import unquote, quote
from starlette.middleware.sessions import SessionMiddleware

# .env 파일의 환경변수 로드
load_dotenv()

app = FastAPI()

# 세션 미들웨어 추가 (비밀키 설정 필요)
session_key = os.getenv("SESSION_KEY")
app.add_middleware(SessionMiddleware, secret_key=session_key)

# 로그 디렉토리 생성
log_dir = "log"
os.makedirs(log_dir, exist_ok=True)  # log 디렉토리가 없으면 생성

# 로깅 설정 (파일에 기록)
logging.basicConfig(
		level=logging.DEBUG,
		format='%(asctime)s - %(levelname)s - %(message)s',
		handlers=[
        logging.FileHandler(os.path.join(log_dir, "app.log")),  # 로그를 log/app.log 파일에 기록
				logging.StreamHandler()          # 콘솔에도 로그 출력
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

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

security = HTTPBasic()

class FileItem(BaseModel):
    name: str

def check_auth(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = os.getenv("USERNAME")
    correct_password = os.getenv("PASSWORD")
    if credentials.username != correct_username or credentials.password != correct_password:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

@app.get("/", response_class=RedirectResponse)
async def redirect_to_dl():
    return RedirectResponse(url="/dl/")

@app.get("/dl/{path:path}", response_class=HTMLResponse)
async def list_files(request: Request, path: str = '', credentials: HTTPBasicCredentials = Depends(check_auth)):
    root_dir = os.getenv("ROOT_DIR")
    directory_path = os.path.join(root_dir, path.lstrip("/")).rstrip("/")  # 선행 슬래시 제거 및 마지막 슬래시 제거
    
    if not os.path.isdir(directory_path):
        raise HTTPException(status_code=404, detail="Directory not found")

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
    parent_path = os.path.dirname(path).rstrip("/")  # 마지막 슬래시 제거

    # 파일이 디렉토리인지 여부 확인
    file_info = [(file.lstrip('/'), os.path.isdir(os.path.join(directory_path, file))) for file in filtered_files]
    print(file_info)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "file_info": file_info,
        "readme_content": readme_content,
        "current_path": path.lstrip('/'),
        "parent_path": parent_path,
        "is_root": (path == '')  # 최상위 경로인지 여부
    })

def check_auth(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = os.getenv("USERNAME")
    correct_password = os.getenv("PASSWORD")
    if credentials.username != correct_username or credentials.password != correct_password:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

@app.get("/download/{path:path}", response_class=FileResponse)
async def download_file(path: str, credentials: HTTPBasicCredentials = Depends(check_auth)):
    path = unquote(path)  # URL 인코딩된 문자열을 디코딩
    logger.debug(f"path=/download/{path}")

    root_dir = os.getenv("ROOT_DIR")

    # 직접 경로 생성 (상대 경로 사용하지 않음) 
    # .relative_to("/")  # 한글파일의 경우 오류 발생(relative_to)
    file_path = os.path.join(root_dir, path.lstrip('/'))  # 선행 슬래시 제거
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    # file 객체 생성
    file = Path(file_path)

    # 파일 이름 추출
    filename = file.name

    # 파일 확장자 추출
    extension = file.suffix

    # MIME 타입 자동 설정
    mime_type, _ = mimetypes.guess_type(file_path) # nginx를 경유하는 경우 비정상

    # 디버깅 정보 로그
    logger.debug(f"media_type={mime_type or 'application/octet-stream'}, file_path={file_path}, filename={filename}, extension={extension}")

    # Content-Disposition 설정
    disposition = 'attachment' # default : 다운로드할 파일
    if extension in ['.pdf', '.txt', '.jpg', '.jpeg', '.png', '.gif']:  # 직접 열 수 있는 파일 형식
        disposition = 'inline'

    # 파일 이름을 UTF-8로 인코딩
    encoded_filename = quote(filename.encode('utf-8'))
    response = FileResponse(file_path, media_type=mime_type or 'application/octet-stream')
    # response.headers["Content-Disposition"] = f'{disposition}; filename="{encoded_filename}"'

    # 캐시 제어 헤더 추가
    # response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    # response.headers["Pragma"] = "no-cache"

    return response

def get_readme_content(path):
    readme_path = os.path.join(path, '.README')
    if os.path.isfile(readme_path):
        with open(readme_path, 'r') as f:
            content = f.readlines()
        return '<br>'.join(line.strip() for line in content if not line.startswith('#'))
    return ""

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST")
    port = int(os.getenv("PORT"))
    uvicorn.run(app, host=host, port=port)
