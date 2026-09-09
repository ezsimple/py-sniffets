#!/usr/bin/env python3
"""초미니 datadog agent: nginx 뒷단 backend 직결 체크 + 텔레그램 알림(시간당 3회 제한).

왜 backend 직결인가: /erp, /calendar 같은 static alias는 backend가 죽어도
nginx가 200을 반환해서 기존 public-URL 방식으론 장애를 감지할 수 없음.
그래서 port backend는 127.0.0.1:port 로, uwsgi는 unix socket connect 로 직접 확인한다.
public 체크는 nginx 매핑 깨짐 감지용으로만 병행한다.

stdlib only. 실행: python3 a1_mon.py (systemd: a1_mon.service 참조)
"""
import json
import os
import socket
import time
import urllib.request
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv('.env.dev')

BASE = "https://a1.mkeasy.kro.kr"
TIMEOUT = 8
INTERVAL = int(os.getenv("CHECK_INTERVAL_SEC", "180"))
STATE_FILE = os.getenv("STATE_FILE", "/tmp/a1_mon_state.json")
MAX_ALERTS_PER_HOUR = 3

# name -> backend 직결 URL("unix:/path" 또는 http) + nginx 경유 public URL(""이면 public 스킵)
SERVICES = {
    "toy-project":  {"backend": "unix:/tmp/toy-project.sock", "public": f"{BASE}/health"},
    "hr-server":    {"backend": "unix:/tmp/hr-server.sock", "public": f"{BASE}/hr/health"},
    "bad":          {"backend": "http://127.0.0.1:3100/", "public": f"{BASE}/bad/"},
    "quotes":       {"backend": "http://127.0.0.1:3355/quotes/health", "public": f"{BASE}/quotes/health"},
    "chat":         {"backend": "http://127.0.0.1:4444/chat/health", "public": f"{BASE}/chat/health"},
    "past-weather": {"backend": "http://127.0.0.1:3366/past-weather/health", "public": f"{BASE}/past-weather/health"},
    "http_auth":    {"backend": "http://127.0.0.1:3333/v1/health", "public": f"{BASE}/v1/health"},
    "rag2":         {"backend": "http://127.0.0.1:8200/rag2/", "public": f"{BASE}/rag2/"},
    "keycloak":     {"backend": "http://127.0.0.1:18080/auth/", "public": f"{BASE}/auth"},
    "holiday":      {"backend": "http://127.0.0.1:3002/holiday", "public": f"{BASE}/holiday"},
    "qr":           {"backend": "http://127.0.0.1:3200/", "public": f"{BASE}/qr/"},
    "kibana":       {"backend": "http://127.0.0.1:5601/kibana/", "public": f"{BASE}/kibana/"},
    "react-erp":    {"backend": "", "public": f"{BASE}/erp"},
    "calendar":     {"backend": "", "public": f"{BASE}/calendar"},
}


def http_ok(url):
    try:
        with urllib.request.urlopen(url, timeout=TIMEOUT) as r:
            return (200 <= r.status < 400, str(r.status))
    except Exception as e:  # ponytail: 상태코드/예외 구분 없이 죽음 하나로 취급
        return (False, str(e)[:100])


def unix_ok(path):
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.settimeout(TIMEOUT)
        s.connect(path)
        s.close()
        return (True, "sock ok")
    except Exception as e:
        return (False, str(e)[:100])


def check(name, cfg):
    """(alive, detail) — backend 죽으면 DOWN, backend 살고 public만 죽으면 NGINX-MAP 문제."""
    b, p = cfg["backend"], cfg["public"]
    if b.startswith("unix:"):
        ok, d = unix_ok(b[5:])
        if not ok:
            return (False, f"backend DOWN ({d})")
    elif b:
        ok, d = http_ok(b)
        if not ok:
            return (False, f"backend DOWN ({d})")
    if p:
        ok, d = http_ok(p)
        if not ok:
            return (False, f"backend OK but nginx-map FAIL ({d})")
    return (True, "ok")


def send_telegram(text):
    token, chat = os.getenv("TELEGRAM_BOT_TOKEN"), os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat:
        print(f"[warn] telegram env 없음, stdout만: {text}")
        return
    data = json.dumps({"chat_id": chat, "text": text}).encode()
    req = urllib.request.Request(f"https://api.telegram.org/bot{token}/sendMessage",
                                 data=data, headers={"Content-Type": "application/json"})
    urllib.request.urlopen(req, timeout=TIMEOUT).read()


def load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except Exception:
        return {}


def save_state(st):
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(st, f)
    except Exception as e:
        print(f"[warn] state 저장 실패: {e}")


def should_alert(st, name, now):
    ts = [t for t in st.get(name, {}).get("alerts", []) if now - t < 3600]
    return len(ts) < MAX_ALERTS_PER_HOUR, ts


def loop_once():
    st = load_state()
    now = time.time()
    for name, cfg in SERVICES.items():
        alive, detail = check(name, cfg)
        prev = st.get(name, {}).get("down", False)
        if not alive and not prev:  # 새로 다운
            ok, ts = should_alert(st, name, now)
            st[name] = {"down": True, "alerts": ts + ([now] if ok else ts)}
            msg = f"[DOWN] {name}: {detail}"
            print(msg, flush=True)
            if ok:
                send_telegram(msg)
            else:
                print(f"[throttle] {name}: 시간당 {MAX_ALERTS_PER_HOUR}회 초과, 알림 생략", flush=True)
        elif not alive and prev:  # 계속 다운: throttle 안에서만 재알림
            ok, ts = should_alert(st, name, now)
            if ok:
                st[name]["alerts"] = ts + [now]
                send_telegram(f"[STILL DOWN] {name}: {detail}")
        elif alive and prev:  # 복구
            st[name] = {"down": False, "alerts": st.get(name, {}).get("alerts", [])}
            msg = f"[RECOVERED] {name} 복구됨"
            print(msg, flush=True)
            send_telegram(msg)
    save_state(st)


if __name__ == "__main__":
    print(f"a1_mon 시작: {len(SERVICES)}개 체크, {INTERVAL}s 간격, 시간당 알림 {MAX_ALERTS_PER_HOUR}회", flush=True)
    while True:
        try:
            loop_once()
        except Exception as e:
            print(f"[err] loop: {e}", flush=True)
        time.sleep(INTERVAL)
