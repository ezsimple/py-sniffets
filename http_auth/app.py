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

# .env 파일의 환경변수 로드
load_dotenv()

app = FastAPI()

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
    file_info = [(file, os.path.isdir(os.path.join(directory_path, file))) for file in filtered_files]

    return templates.TemplateResponse("index.html", {
        "request": request,
        "file_info": file_info,
        "readme_content": readme_content,
        "current_path": path,
        "parent_path": parent_path,
        "is_root": (path == '')  # 최상위 경로인지 여부
    })

@app.get("/download/{path:path}")
async def download_file(path: str, credentials: HTTPBasicCredentials = Depends(check_auth)):
    root_dir = os.getenv("ROOT_DIR")

    file_path = Path(root_dir) / Path(path).relative_to("/")  # 안전하게 경로 생성
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    # 파일 이름 추출
    filename = file_path.name
    # MIME 타입 자동 설정
    mime_type, _ = mimetypes.guess_type(file_path)

    # MIME 타입에 따라 직접 표시하도록 설정
    response = FileResponse(file_path, media_type=mime_type or 'application/octet-stream')

    return response

    # file_path = os.path.join(root_dir, path.lstrip("/")).rstrip("/")  # 마지막 슬래시 제거
		#
    # if not os.path.isfile(file_path):
    #    raise HTTPException(status_code=404, detail="File not found")
		#
    # return FileResponse(file_path, media_type='application/octet-stream')

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
