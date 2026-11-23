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
DEFAULT_MODEL = "@cf/black-forest-labs/flux-1-schnell"  # 무료. 카탈로그상 무료 Text-to-Image 중 유일한 현역
LLM_TRANSLATE_MODEL = "@cf/meta/llama-3.1-8b-instruct"  # 무료, 디자인 용어 이해용
TRANSLATE_MODEL = "@cf/meta/m2m100-1.2b"  # 폴백용 무료 번역 모델

# 디자인/웹디자인/전공 용어 오역 방지용 시스템 프롬프트.
TRANSLATE_SYSTEM = (
    "You are a professional translator for designers and design students. "
    "Translate Korean to English for image generation. "
    "Use exact design terms. Glossary: 수채화=watercolor illustration, "
    "창가 자리=window seat, 따뜻한 조명=warm cozy lighting, "
    "여백=negative space, 그리드=grid layout, 타이포그래피=typography, "
    "목업=mockup, 와이어프레임=wireframe, 히어로 섹션=hero section, "
    "카드 UI=card UI, 반응형=responsive, 질감=texture, 구도=composition, "
    "색감=color palette, 톤앤매너=tone and manner. "
    "Output English translation only, no explanation, no quotes."
)

# 한글 요청 의도가 영어 프롬프트에서 깨지지 않도록 강제하는 가드 구간.
# 이유: 이전 실패처럼 Seoul이 일본어풍 간판으로 오염되는 것을 MCP에서 1회 차단.
KOREA_GUARD = (
    ", Scene location is Seoul, South Korea. "
    "All visible shop signs and text must be in correct Korean Hangul only "
    "(e.g. 카페, 커피), absolutely no Japanese kana, no Japanese kanji style, "
    "no Chinese-only text, no gibberish letters, keep text short and legible"
)


def _cf_run(model: str, payload: dict, timeout: int = 30) -> dict:
    # Workers AI 공용 호출 함수 (번역/이미지 모두 사용).
    url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run/{model}"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _translate_ko_to_en(text: str) -> str:
    # 한글 포함 시 무료 LLM으로 KO->EN 변환, 실패 시 m2m100→원문 순 폴백.
    if not any("\uac00" <= ch <= "\ud7a3" for ch in text):
        return text
    try:
        data = _cf_run(
            LLM_TRANSLATE_MODEL,
            {
                "messages": [
                    {"role": "system", "content": TRANSLATE_SYSTEM},
                    {"role": "user", "content": text},
                ]
            },
            timeout=45,
        )
        out = (
            data.get("result", {}).get("response")
            or data.get("result", {}).get("text")
            or ""
        )
        # choices 포맷 변형 대응
        if not out:
            choices = data.get("result", {}).get("choices", [])
            if choices:
                out = choices[0].get("message", {}).get("content", "")
        out = out.strip().strip('"').strip()
        if out and any("\uac00" <= ch <= "\ud7a3" for ch in out):
            out = ""  # 번역 실패로 간주
        if out:
            return out
    except Exception:
        pass
    try:
        data = _cf_run(
            TRANSLATE_MODEL,
            {"text": text, "source_lang": "korean", "target_lang": "english"},
        )
        out = data.get("result", {}).get("translated_text") or ""
        out = out.strip() if out.strip() else text
        # m2m100 단골 오역 보정 (수채화->aquarium).
        if "수채화" in text and "aquarium" in out.lower():
            out = out.replace("aquarium", "watercolor").replace(
                "Aquarium", "Watercolor"
            )
        return out
    except Exception:
        return text


def _augment(prompt: str) -> str:
    p = prompt.strip()
    low = p.lower()
    has_hangul = any("\uac00" <= ch <= "\ud7a3" for ch in p)
    korea_hint = has_hangul or any(
        k in low for k in ["seoul", "korea", "hangul", "korean", "카페", "서울"]
    )
    if korea_hint and "no japanese" not in low:
        p = p + KOREA_GUARD
    return p


@mcp.tool()
def generate_image(
    prompt: str,
    output_path: str = "",
    steps: int = 8,
    model: str = DEFAULT_MODEL,
    seed: int = 0,
) -> str:
    """
    Cloudflare Workers AI를 사용해 이미지를 생성하고 로컬 파일로 저장합니다.
    - prompt: 한국어 또는 영어 이미지 설명 (한글 포함 시 무료 번역 모델로 EN 변환 후 생성)
    - output_path: 저장할 PNG 파일 경로 (비워두면 현재 작업 디렉토리에 자동 저장)
    - steps: 8 고정 권장 (schnell 최대, 무료 모델 품질 상한)
    - model: 이미지 모델 ID (무료는 schnell만 현역, 나머지는 유료/퇴출)
    - seed: 0이면 랜덤, 재현이 필요하면 양의 정수
    """
    if not ACCOUNT_ID or not API_TOKEN:
        return "오류: CLOUDFLARE_ACCOUNT_ID 또는 CLOUDFLARE_API_TOKEN 환경변수가 설정되지 않았습니다."

    url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run/{model}"
    orig_low = prompt.lower()
    orig_korea = any("\uac00" <= ch <= "\ud7a3" for ch in prompt) or any(
        k in orig_low for k in ["seoul", "korea", "카페", "서울"]
    )
    prompt = _augment(_translate_ko_to_en(prompt))
    if orig_korea and "no japanese" not in prompt.lower():
        prompt = prompt + KOREA_GUARD
    # 무료 schnell 스펙: prompt(최대 2048자)+steps(최대 8)+seed만 지원.
    payload: dict = {
        "prompt": prompt[:2000],
        "steps": max(1, min(steps or 8, 8)),
    }
    if seed:
        payload["seed"] = seed
    timeout = 90

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
        with urllib.request.urlopen(req, timeout=timeout) as resp:
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

