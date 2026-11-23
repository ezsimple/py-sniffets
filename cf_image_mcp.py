import base64
import json
import os
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("cloudflare-image-gen")

ACCOUNT_ID = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "")
API_TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN", "")
DEFAULT_MODEL = "@cf/black-forest-labs/flux-1-schnell"


@mcp.tool()
def generate_image(
    prompt: str,
    output_path: str = "",
    steps: int = 4,
    model: str = DEFAULT_MODEL,
) -> str:
    """
    Cloudflare Workers AI를 사용해 이미지를 생성하고 로컬 파일로 저장합니다.
    - prompt: 영어로 번역 및 구체화된 이미지 생성 프롬프트
    - output_path: 저장할 PNG 파일 경로 (비워두면 현재 작업 디렉토리에 자동 저장)
    - steps: 생성 스텝 수 (flux-1-schnell 기준 4~8 권장, 최대 8)
    - model: Cloudflare Workers AI 이미지 모델 ID
    """
    if not ACCOUNT_ID or not API_TOKEN:
        return "오류: CLOUDFLARE_ACCOUNT_ID 또는 CLOUDFLARE_API_TOKEN 환경변수가 설정되지 않았습니다."

    url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run/{model}"
    payload = {
        "prompt": prompt,
        "steps": max(1, min(steps, 8)),
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            content_type = resp.headers.get("Content-Type", "")
            raw_bytes = resp.read()

            if "application/json" in content_type:
                data = json.loads(raw_bytes.decode("utf-8"))
                b64_img = data.get("result", {}).get("image")
                if not b64_img:
                    return f"오류: 응답에 이미지 데이터가 없습니다. 응답: {data}"
                image_bytes = base64.b64decode(b64_img)
            else:
                image_bytes = raw_bytes

    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        return f"HTTP 오류 ({e.code}): {err_body}"
    except Exception as e:
        return f"요청 실패: {str(e)}"

    if not output_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"generated_{timestamp}.png"

    target = Path(output_path).expanduser().resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(image_bytes)

    return f"이미지 생성 완료: {target}"


if __name__ == "__main__":
    mcp.run()

