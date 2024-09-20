from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List

HOST = '127.0.0.1'
PATH = 'static'
PORT = 5000

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# 이미지 데이터 모델
class Image(BaseModel):
    filename: str

# 이미지 목록
images = [
    Image(filename=f"{PATH}/image1.jpg"),
    Image(filename=f"{PATH}/image2.jpg"),
    Image(filename=f"{PATH}/image3.jpg")
]

# 정적 파일 제공
app.mount("/static", StaticFiles(directory="static"), name="static")

# 미들웨어 정의
@app.middleware("http")
async def add_gallery_middleware(request: Request, call_next):
    if request.url.path == "/":
        response = templates.TemplateResponse("gallery.html", {"request": request, "images": images})
        return response
    response = await call_next(request)
    return response

# 애플리케이션 실행 시 사용
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)

