from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware import Middleware
from common import exception
from common.config import settings
from control import route
from model.model import LoginMiddleWare

'''
순서가 중요합니다. SessionMiddleWare가 항상 먼저 와야합니다.
'''
middleware = [
    Middleware(SessionMiddleware, secret_key=settings.JWT_SECRET),
    Middleware(LoginMiddleWare),
    Middleware(
      CORSMiddleware,
      allow_origins=["*"],  # 모든 도메인 허용, 필요에 따라 수정
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
    )
]

app = FastAPI(middleware=middleware)

# 정적 파일 디렉토리 설정
app.mount("/static", StaticFiles(directory="static"), name="static")

# 예외 핸들러 등록
app.add_exception_handler(HTTPException, exception.http_exception_handler)

# 라우터 등록
app.include_router(route.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
