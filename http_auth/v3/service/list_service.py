import os
from fastapi import HTTPException
from core.config import settings

async def get_file_list():
    try:
        files = os.listdir(settings.ROOT_DIR)
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
