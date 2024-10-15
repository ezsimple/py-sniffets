from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from .auth import verify_token
from service import download_service, list_service, login_service

router = APIRouter()

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    return await login_service.login(form_data.username, form_data.password)

@router.get("/files")
async def get_files(token: str = Depends(verify_token)):
    return await list_service.get_file_list()

@router.post("/download/{file_name}")
async def download_file(file_name: str, token: str = Depends(verify_token)):
    return await download_service.download_file(file_name)
