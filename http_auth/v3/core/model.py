from pydantic import BaseModel
from datetime import datetime
import json
from fastapi import Request, Response, HTTPException,status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse, HTMLResponse
from jose import JWTError, jwt
from .config import settings
from .route import templates

class User(BaseModel):
    username: str
    email: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str

class LoginMiddleWare(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/v3/files":
            pass

        # 요청 경로 확인
        if await self.verify_ignored_paths(request):
            return await call_next(request)

        if not request.url.path.startswith(settings.PREFIX):
            return Response("Unauthorized", status_code=status.HTTP_401_UNAUTHORIZED)

        token = await self.find_token(request)
        if not token:
            return RedirectGetResponse(url=f"{settings.PREFIX}/login")

        try:
            # 토큰 검증
            payload = self.verify_token(token)
            request.state.user = payload  # 사용자 정보를 요청 상태에 저장
        except HTTPException as e:
            return Response("Unauthorized", status_code=e.status_code)

        response = await call_next(request)
        return response

    async def verify_ignored_paths(self, request: Request) -> bool:
        uri = request.url.path
        if uri.startswith("/static/") or uri == '/favicon.ico':
            return True

        ignored_paths = [
            f"{settings.PREFIX}/token",
            f"{settings.PREFIX}/login",
            f"{settings.PREFIX}/logout",
            f"{settings.PREFIX}",
            f"{settings.PREFIX}/",
        ]
        return any(uri == path for path in ignored_paths)

    async def find_token(self, request: Request) -> str:
        if request.url.path == "/v3/files":
            pass

        # 1. Authorization 헤더에서 토큰 확인
        token = request.headers.get("Authorization")
        if token and token.startswith("Bearer "):
            return token.split(" ")[1]  # "Bearer <token>" 형식에서 실제 토큰만 반환

        # 2. 쿠키에서 토큰 확인
        token = request.cookies.get("token")
        if token:
            token = token.replace("'", '"')
            json_dict = json.loads(token)  
            return json_dict.get('access_token')  # 쿠키에서 가져온 토큰 반환

        return None

    def verify_token(self, token: str):
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
            return payload
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    @staticmethod
    async def clear_session(request: Request, response: Response):
        '''
        세션 클리어 로직을 여기에 구현
        '''
        request.session.pop('username', None)
        response.delete_cookie("token")

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
        # is_logined = "username" in context.get("request").session
        # context["is_logined"] = is_logined 

        super().__init__(content=templates.get_template(template_name).render(context))