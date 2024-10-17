from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.security import OAuth2PasswordRequestForm
from service import download_service, files_service, login_service
from common.auth import verify_token
from common.config import settings, templates
from model.model import LoginMiddleWare, CustomTemplateResponse, RedirectGetResponse

router = APIRouter(prefix=settings.PREFIX)

@router.get("/login", response_class=HTMLResponse)
async def view_login(request: Request) -> HTMLResponse:
    return CustomTemplateResponse("login.html", {"request": request})

@router.post("/login", response_class=HTMLResponse)
async def ok_login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()) -> HTMLResponse:

    token = await login_service.login(form_data.username, form_data.password)
    if token:
        '''
        POST -> Rediect -> GET
        '''
        response = RedirectGetResponse(url=f"{settings.PREFIX}/files")
        response.set_cookie(key="token", value=token)  # 토큰을 쿠키에 저장
        return response
        
    return CustomTemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})

@router.api_route("/logout", methods=["GET", "POST"], response_class=HTMLResponse)
async def logout(request: Request, response: Response):
    response = RedirectGetResponse(url=f"{settings.PREFIX}/login")
    response.delete_cookie('token')
    return response

@router.get("/", response_class=RedirectResponse)
async def redirect_to_files():
    return RedirectGetResponse(url=f"{settings.PREFIX}/files")

@router.post("/token")
async def token(form_data: OAuth2PasswordRequestForm = Depends()) -> dict:
    return await login_service.login(form_data.username, form_data.password)

@router.get("/files")
async def view_files(request: Request) -> HTMLResponse:
    return CustomTemplateResponse("files.html", {"request": request })

# @router.post("/files")
# async def list_files(token: str = Depends(verify_token)) -> dict:
#     return await files_service.get_file_list()

@router.post("/download/{path: path}", response_class=FileResponse)
async def download_file(request: Request, path: str, token: str = Depends(verify_token)):
    return await download_service.download_file(request, path)
