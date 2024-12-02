#!/bin/bash
# Hot Reload

HOST=127.0.0.1
PORT=3333
PID=$(lsof -ti :${PORT})
if [ -n "$PID" ]; then
	kill -9 "$PID"
fi
python -m uvicorn app:app --host $HOST --port $PORT --reload
