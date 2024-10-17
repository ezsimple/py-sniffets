import os
import re
from fastapi import HTTPException, status, Request
from fastapi.responses import HTMLResponse
from common.config import settings, logger
from model.model import CustomTemplateResponse

def get_readme_content(path):
    readme_path = os.path.join(path, '.README')
    if os.path.isfile(readme_path):
        with open(readme_path, 'r') as f:
            content = f.readlines()
        return '<br>'.join(line.strip() for line in content if not line.startswith('#'))
    return ""

def get_ignored_patterns(directory_path: str):
    ignore_file_path = os.path.join(directory_path, '.ignorefiles')
    ignored_patterns = []

    if os.path.isfile(ignore_file_path):
        with open(ignore_file_path, 'r') as f:
            ignored_patterns = [line.strip() for line in f if line.strip()]

    return ignored_patterns

async def get_file_list(request: Request, path: str) -> HTMLResponse:
    root_dir = os.getenv("ROOT_DIR")
    directory_path = os.path.join(root_dir, path.lstrip("/")).rstrip("/")  # 선행 슬래시 제거 및 마지막 슬래시 제거

    if not os.path.isdir(directory_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Directory not found")

    files = os.listdir(directory_path)
    ignored_patterns = get_ignored_patterns(directory_path)

    regex_patterns = [re.escape(pattern).replace(r'\*', '.*') for pattern in ignored_patterns]
    filtered_files = [file for file in files if not any(re.match(pattern, file) for pattern in regex_patterns)]

    readme_content = get_readme_content(directory_path)

    parent_path = ""
    if path:
        parent_path = os.path.dirname(path).rstrip("/")

    full_path = path
    remaining_path = full_path.replace(root_dir, "", 1).lstrip("/")
    has_parent = bool(remaining_path)

    logger.debug(f'has_parent={has_parent}, remaining_path={remaining_path}, full_path={full_path}')

    file_info = [(file.lstrip('/'), os.path.isdir(os.path.join(directory_path, file))) for file in filtered_files]
    directories = [(file, is_dir) for file, is_dir in file_info if is_dir]
    files = [(file, is_dir) for file, is_dir in file_info if not is_dir]

    file_info = sorted(directories) + sorted(files)
    current_path = path.lstrip('/').rstrip('/')

    return CustomTemplateResponse("files.html", {
        "request": request,
        "file_info": file_info,
        "readme_content": readme_content,
        "current_path": current_path,
        "parent_path": parent_path,
        "is_root": (path == ''),
        "has_parent": has_parent,
    })
