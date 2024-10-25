from fastapi import status
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse, HTMLResponse
from starlette.requests import Request
from datetime import datetime
from core.config import PREFIX, SESSION_SERVER, SESSION_TIMEOUT, SECRET_KEY, templates
import aioredis
import jwt

# Redis 클라이언트 초기화
redis_client = aioredis.from_url(SESSION_SERVER)

# (중요) SessionMiddleWare가 가장 먼저 호출되어야 함.
class LoginRequiredMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):

        if request.url.path.startswith(f"{PREFIX}/login") \
                or request.url.path.startswith(f"{PREFIX}/token") \
                or request.url.path.startswith("/static/"):
            response = await call_next(request)
            return response

        # 쿠키에서 session_id 가져오기
        is_logined = False
        session_id = request.cookies.get("session_id")
        if session_id and await redis_client.exists(f"session:{session_id}"):
            try:
                access_token = request.session["access_token"]
                await redis_client.expire(f"session:{session_id}", SESSION_TIMEOUT)
                await redis_client.expire(access_token, SESSION_TIMEOUT)  # 세션 연장
                payload = jwt.decode(access_token, SECRET_KEY, algorithms=["HS256"])
                # username = payload.get("sub")
                # request.state.user = User(username=username)    
                is_logined = True
            except jwt.PyJWTError:
                return RedirectGetResponse(url=f"{PREFIX}/login")

        if not is_logined:
            return RedirectGetResponse(url=f"{PREFIX}/login")

        response = await call_next(request)
        return response

class User(BaseModel):
    username: str

class Token(BaseModel):
    access_token: str
    token_type: str

class LoginForm(BaseModel):
    username: str
    password: str

class RedirectGetResponse(RedirectResponse):
    def __init__(self, url: str, **kwargs):
        # status_code를 303으로 설정
        # 302: 일시적 리다이렉션, 원래 HTTP 메서드를 유지.
        # 303: 리소스가 다른 URI에 있으며, GET 메서드를 사용하여 요청해야 함.
        # 307 Temporary Redirect: 요청한 리소스가 일시적으로 다른 URI로 이동했으며, 클라이언트는 원래의 HTTP 메서드를 유지해야 합니다. 
        super().__init__(url=url, status_code=status.HTTP_303_SEE_OTHER, **kwargs)

class CustomTemplateResponse(HTMLResponse):
    def __init__(self, template_name: str, context: dict):
        # 현재 타임스탬프를 context에 추가
        context["timestamp"] = datetime.now().timestamp() 

        # 로그인 상태 확인
        is_logined = "session_id" in context.get("request").cookies
        context["is_logined"] = is_logined 

        super().__init__(content=templates.get_template(template_name).render(context))