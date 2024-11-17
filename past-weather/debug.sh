#!/bin/bash
# Hot Reload
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo ".env 파일이 존재하지 않습니다."
    exit 1
fi

PID=$(lsof -ti :$PORT)
if [ -n "$PID" ]; then
	kill -9 "$PID"
fi
python -m uvicorn app:app --host $HOST --port $PORT --reload
