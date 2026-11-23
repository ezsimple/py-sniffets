import base64
import json
import os
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("gemini-image-gen")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
DEFAULT_MODEL = "google/gemini-nano-banana-2.1"  # 가성비 1순위: Elo 1175(8위) with flash-lite와 동일 단가 $30/1M 이미지토큰


def _fetch_gemini(prompt: str, model: str) -> bytes:
    # Google AI Studio 키로 직접 호출 (OpenRouter 수수료 우회). 모델 ID는 google/ 접두사 제거.
    model_id = model.split("/")[-1]
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]},
    }
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent",
        data=json.dumps(payload).encode("utf-8"),
        headers={"x-goog-api-key": GEMINI_API_KEY, "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    parts = ((data.get("candidates") or [{}])[0].get("content") or {}).get("parts") or []
    for part in parts:
        inline = part.get("inlineData") or {}
        if inline.get("data"):
            return base64.b64decode(inline["data"])
    raise RuntimeError(f"응답에 이미지가 없습니다: {str(data)[:300]}")


def _fetch_openrouter(prompt: str, model: str) -> bytes:
    # GEMINI_API_KEY 부재 시 폴백 (기존 경로 유지)
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "modalities": ["image", "text"],
    }
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "X-Title": "opencode-gemini-image",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    msg = data.get("choices", [{}])[0].get("message", {})
    for im in msg.get("images", []) or []:
        u = (im.get("image_url") or {}).get("url", "")
        if u.startswith("data:"):
            return base64.b64decode(u.split(",", 1)[1])
    raise RuntimeError(f"응답에 이미지가 없습니다: {str(data)[:300]}")


@mcp.tool()
def generate_image(
    prompt: str,
    output_path: str = "",
    model: str = DEFAULT_MODEL,
) -> str:
    """
    Gemini 이미지 생성 모델로 이미지를 만들고 로컬 파일로 저장합니다.
    - GEMINI_API_KEY가 있으면 Google API 직접 호출, 없으면 OpenRouter로 폴백
    - prompt: 한국어 또는 영어 이미지 설명 (Gemini가 한국어 직접 이해, 번역 불필요)
    - output_path: 저장할 PNG 파일 경로 (비워두면 현재 작업 디렉토리에 자동 저장)
    - model: 이미지 모델 ID (기본 3.1-flash-lite, 고화질은 google/gemini-3-pro-image)
    """
    if GEMINI_API_KEY:
        fetch, via = _fetch_gemini, "gemini-direct"
    elif OPENROUTER_API_KEY:
        fetch, via = _fetch_openrouter, "openrouter"
    else:
        return "오류: GEMINI_API_KEY 또는 OPENROUTER_API_KEY 환경변수가 설정되지 않았습니다."

    try:
        image_bytes = fetch(prompt, model)
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        # Gemini 선불 크레딧 소진(402)이면 OpenRouter로 자동 폴백
        if via == "gemini-direct" and e.code == 402 and OPENROUTER_API_KEY:
            try:
                image_bytes = _fetch_openrouter(prompt, model)
                via = "openrouter-fallback"
            except urllib.error.HTTPError as e2:
                return f"폴백 HTTP 오류 ({e2.code}): {e2.read().decode('utf-8', errors='replace')[:300]}"
            except Exception as e2:
                return f"폴백 요청 실패: {str(e2)}"
        else:
            return f"HTTP 오류 ({e.code}): {err_body[:300]}"
    except Exception as e:
        return f"요청 실패: {str(e)}"

    if not output_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"generated_{timestamp}.png"

    target = Path(output_path).expanduser().resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(image_bytes)

    return f"이미지 생성 완료 ({via}): {target}"


if __name__ == "__main__":
    mcp.run()
