import os
from fastapi import HTTPException
from core.config import settings

async def download_file(file_name: str):
    file_path = os.path.join(settings.ROOT_DIR, file_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return {"file_path": file_path}
