from fastapi import FastAPI, HTTPException
from core import route, exception
from core.config import settings

app = FastAPI()

# 예외 핸들러 등록
app.add_exception_handler(HTTPException, exception.http_exception_handler)

# 라우터 등록
app.include_router(route.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
