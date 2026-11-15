#!/usr/bin/env python3
"""텔레그램 알림 SSOT 모듈 (stdlib only, cron 안전).

- import 시점에 .env.dev -> .env -> ~/.env 순으로 로드 (기존값 우선, cron env 비어있음 대비)
- 실패해도 raise 없이 False 반환 + stderr 경고 (크론 무음 실패 방지)
- 사용: from telegram import send_telegram
"""
import json
import os
import sys
import urllib.request

TIMEOUT: int = 10
MAX_LEN: int = 4096  # Bot API text 상한

_ENV_FILES = (
    os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env.dev"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"),
    os.path.expanduser("~/.env"),
)


def _load_env() -> None:
    for path in _ENV_FILES:
        try:
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        os.environ.setdefault(k.strip(), v.strip().strip("\"'"))
        except FileNotFoundError:
            continue
        except OSError as e:
            print(f"[warn] env 읽기 실패 {path}: {e}", file=sys.stderr)


_load_env()


def send_telegram(message: str, timeout: int = TIMEOUT) -> bool:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat:
        print(f"[warn] TELEGRAM env 없음, 발송 생략: {message[:200]}", file=sys.stderr)
        return False
    # ponytail: API 4096자 제한, 초과분 절단 (분할발송은 필요해지면 추가)
    text = message[:MAX_LEN]
    data = json.dumps({"chat_id": chat, "text": text}).encode()
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            if json.loads(r.read().decode()).get("ok"):
                return True
            print("[warn] telegram API ok=false", file=sys.stderr)
            return False
    except Exception as e:
        print(f"[warn] telegram 발송 실패: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    msg = sys.argv[1] if len(sys.argv) > 1 else "telegram module self-check ok"
    sys.exit(0 if send_telegram(msg) else 1)
