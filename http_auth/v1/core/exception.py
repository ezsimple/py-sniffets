from fastapi import Request, HTTPException, status
from core.config import PREFIX, logger
from core.model import RedirectGetResponse

# HTTPException 처리기
async def http_exception_handler(request: Request, exc: HTTPException):
    # 예외 로그 기록
    logger.error(f"HTTPException occurred: {exc.detail}, Status code: {exc.status_code}, Path: {request.url.path}")
    # if exc.status_code == status.HTTP_401_UNAUTHORIZED:
    #     return { "error": "Unauthorized", "detail": "Incorrect username or password" }, status.HTTP_401_UNAUTHORIZED
    return RedirectGetResponse(url=f"{PREFIX}/login")

# ValueError 처리기
async def value_error_handler(request: Request, exc: ValueError):
    # 예외 로그 기록
    logger.error(f"ValueError occurred: {exc}, Path: {request.url.path}")
    return RedirectGetResponse(url=f"{PREFIX}/login")  # 추후 에러페이지로