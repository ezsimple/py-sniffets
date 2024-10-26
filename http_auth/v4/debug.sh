#!/bin/bash
# Hot Reload

PID=$(lsof -ti :3333)
if [ -n "$PID" ]; then
	kill -9 "$PID"
fi
python -m uvicorn app:app --host 127.0.0.1 --port 3333 --reload
