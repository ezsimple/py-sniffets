from fastapi import HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse, HTMLResponse
from starlette.requests import Request
from starlette.responses import Response
from pydantic import BaseModel
from datetime import datetime
from core.config import PREFIX, logger, verify_token, templates

# (중요) SessionMiddleWare가 가장 먼저 호출되어야 함.
# JWT 인증 확인
import pdb
class LoginRequiredMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 로그인, 로그아웃 페이지 요청은 무시
        ignored_paths = [
            "/static/",
            f"{PREFIX}/login",
            f"{PREFIX}/logout",
            f"{PREFIX}",
            f"{PREFIX}/"
        ]
        if any(request.url.path.startswith(path) for path in ignored_paths):
            return await call_next(request)
        
        # 인증 시도
        username = await self.authenticate(request)
        if username:
            request.session["username"] = username  # 세션에 사용자명 저장
            logger.debug(f"미들웨어: 인증된 사용자: {username}")
        else:
            return RedirectGetResponse(url=f"{PREFIX}/login")

        # 다음 미들웨어 또는 요청 처리기로 넘어감
        response = await call_next(request)
        return response

    async def authenticate(self, request: Request):
        # 1. 쿠키에서 토큰 검사
        access_token = request.cookies.get("access_token")
        if access_token:
            try:
                return verify_token(access_token)  # 쿠키에서 인증
            except HTTPException:
                logger.debug("쿠키에서 토큰 검증 실패")

        # 2. 세션에서 로그인 상태 확인
        if "username" in request.session:
            return request.session["username"]

        # 3. 헤더에서 토큰 검사
        return await self.verify_header(request)

    async def verify_header(self, request: Request):
        # Authorization 헤더에서 Bearer 토큰 추출
        auth: str = request.headers.get("Authorization")
        if auth is None:
            # Authorization 헤더가 없으면 로그인 페이지로 리다이렉트
            # FastAPI의 미들웨어에서 발생한 예외는 기본적으로 라우터로 전달되지 않으며, 예외 핸들러가 이를 처리하지 않습니다.
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header missing")

        token = auth.split(" ")[1]  # 'Bearer <token>' 형식에서 토큰 추출
        return verify_token(token)  # 토큰 검증
    
    @staticmethod
    async def clear_session(request: Request, response: Response):
        """세션에서 사용자 정보를 제거하는 메서드"""
        request.session.pop('username', None)
        response.delete_cookie("access_token")  # 쿠키에서 access_token 제거
        logger.debug("로그아웃: 세션에서 사용자 정보 제거")


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
        is_logined = "username" in context.get("request").session
        context["is_logined"] = is_logined 

        super().__init__(content=templates.get_template(template_name).render(context))