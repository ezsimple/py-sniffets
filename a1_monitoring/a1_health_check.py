from typing import List, Tuple
import httpx
import time
import os
import sys

from telegram import send_telegram


# -----------------------------
# 설정값 (반드시 초기화)
# -----------------------------
BASE_URL: str = os.getenv("A1_BASE_URL", "https://a1.mkeasy.kro.kr")

ENDPOINTS: List[str] = [
    "/chat/",
    "/rag2/",
    "/v1/",
    "/quotes/health",
    "/holiday",
]

TIMEOUT_SECONDS: int = int(os.getenv("HEALTH_TIMEOUT_SEC", "5"))
RETRY_COUNT: int = int(os.getenv("HEALTH_RETRY_COUNT", "2"))

# -----------------------------
# 헬스체크
# -----------------------------
def check_endpoint(client: httpx.Client, path: str) -> Tuple[str, bool, str]:
    url: str = BASE_URL + path
    last_err: str = ""

    for _ in range(RETRY_COUNT):
        try:
            response: httpx.Response = client.get(url, timeout=TIMEOUT_SECONDS)
            if 200 <= response.status_code < 400:
                return (path, True, f"{response.status_code}")
            last_err = f"HTTP {response.status_code}"
        except Exception as e:
            last_err = str(e)[:200]
    return (path, False, last_err)


# -----------------------------
# 메인 로직 (실패 시 exit 1 — cron이 실패를 감지)
# -----------------------------
def a1_health_check() -> None:
    failed: List[str] = []

    with httpx.Client() as client:
        for ep in ENDPOINTS:
            path: str
            ok: bool
            reason: str

            path, ok, reason = check_endpoint(client, ep)

            if not ok:
                failed.append(f"{path} -> {reason}")

    if failed:
        now: str = time.strftime("%Y-%m-%d %H:%M:%S")

        message: str = "[ALERT] 서비스 장애 발생\n"
        message += f"시간: {now}\n\n"
        message += "\n".join(failed)

        send_telegram(message)
        print(message, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    a1_health_check()
