#!/bin/bash
# Hot Reload

HOST=127.0.0.1
PORT=3333

# fuser 기반 kill (더 확실)
fuser -k ${PORT}/tcp 2>/dev/null

# uvicorn 관련 전체 종료 (reload 대응)
pkill -f "uvicorn app:app" 2>/dev/null

sleep 1

python -m uvicorn app:app --host $HOST --port $PORT --reload
