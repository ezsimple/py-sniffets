import os
from datetime import datetime
from fastapi import status
from starlette.responses import RedirectResponse, HTMLResponse
from fastapi import status
from starlette.responses import RedirectResponse, HTMLResponse
from datetime import datetime
from core.config import templates
from core.util import get_readme_content

class RedirectGetResponse(RedirectResponse):
    def __init__(self, url: str, **kwargs):
        # status_code를 303으로 설정
        # 302: 일시적 리다이렉션, 원래 HTTP 메서드를 유지.
        # 303: 리소스가 다른 URI에 있으며, GET 메서드를 사용하여 요청해야 함.
        # 307 Temporary Redirect: 요청한 리소스가 일시적으로 다른 URI로 이동했으며, 클라이언트는 원래의 HTTP 메서드를 유지해야 합니다.
        super().__init__(url=url, status_code=status.HTTP_303_SEE_OTHER, **kwargs)

class CustomTemplateResponse(HTMLResponse):
    def __init__(self, template_name: str, context: dict):

        root_dir = os.getcwd()
        directory_path = os.path.join(root_dir, "")
        context['readme'] = get_readme_content(directory_path)
        context["timestamp"] = datetime.now().timestamp()

        super().__init__(content=templates.get_template(template_name).render(context))