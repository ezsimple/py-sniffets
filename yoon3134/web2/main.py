from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List

HOST = '127.0.0.1'
PORT = 5000

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# 이미지 데이터 모델
class Image(BaseModel):
    filename: str

# 이미지 목록
images = [
    Image(filename="image1.jpg"),
    Image(filename="image2.jpg"),
    Image(filename="image3.jpg")
]

# 정적 파일 제공
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_gallery(request: Request):
    return templates.TemplateResponse("gallery.html", {"request": request, "images": images})

# 애플리케이션 실행 시 사용
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)

