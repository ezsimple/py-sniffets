#!/bin/bash

# 1. .env 파일에서 환경 변수 로드
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo ".env 파일이 존재하지 않습니다."
    exit 1
fi

# 2. 기존 프로세스를 찾아서 kill
# fuser 기반 kill (더 확실)
fuser -k ${PORT}/tcp 2>/dev/null

# uvicorn 관련 전체 종료 (reload 대응)
#pkill -f "uvicorn app:app" 2>/dev/null
if [ -f .uvicorn.pid ]; then
    PGID=$(cat .uvicorn.pid)
    kill -TERM -$PGID 2>/dev/null
fi
sleep 1

# 3. nohup.out 존재하면 삭제
if [ -f nohup.out ]; then
    echo "nohup.out 파일을 삭제합니다."
    rm nohup.out
fi

# 4. nohup을 이용하여 FastAPI 애플리케이션 실행
echo "애플리케이션이 백그라운드에서 실행 중입니다."
nohup setsid python -m uvicorn app:app \
  --host ${HOST} \
  --port ${PORT} \
  --reload \
  > uvicorn.log 2>&1 &
echo $! > .uvicorn.pid
