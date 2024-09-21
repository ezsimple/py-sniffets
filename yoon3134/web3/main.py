from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from core.route import router as api_router

app = FastAPI()
templates = Jinja2Templates(directory="templates")  # 템플릿 디렉토리 설정

# 정적 파일 라우팅
app.mount("/static", StaticFiles(directory="static"), name="static")

# API 라우터 포함
app.include_router(api_router)

# 기본 라우트
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("page1.html", {"request": request})

# 리다이렉션 예제
@app.get("/redirect")
async def redirect_example():
    return RedirectResponse(url="/gallery")


# 애플리케이션 실행 시 사용
if __name__ == "__main__":
	  import uvicorn
	  HOST = '127.0.0.1'
	  PORT = 5000
	  uvicorn.run(app, host=HOST, port=PORT)
