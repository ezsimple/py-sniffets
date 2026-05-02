from typing import List, Tuple
import httpx
import time
import os


# -----------------------------
# 설정값 (반드시 초기화)
# -----------------------------
BASE_URL: str = "https://a1.mkeasy.kro.kr"

ENDPOINTS: List[str] = [
    "/chat/",
    "/rag1/",
    "/rag2/",
    "/v1/",
    "/quotes",
    "/holiday",
]

TELEGRAM_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID")
TIMEOUT_SECONDS: int = 5

# -----------------------------
# 헬스체크
# -----------------------------
def check_endpoint(client: httpx.Client, path: str) -> Tuple[str, bool, str]:
    url: str = BASE_URL + path

    try:
        response: httpx.Response = client.get(url, timeout=TIMEOUT_SECONDS)
        if response.status_code >= 200 and response.status_code < 400:
            return (path, True, f"{response.status_code}")
        return (path, False, f"HTTP {response.status_code}")
    except Exception as e:
        return (path, False, str(e))


# -----------------------------
# 텔레그램 전송
# -----------------------------
def send_telegram(message: str) -> None:
    url: str = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload: dict = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
    }

    with httpx.Client() as client:
        client.post(url, json=payload)


# -----------------------------
# 메인 로직
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


if __name__ == "__main__":
    a1_health_check()