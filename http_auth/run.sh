#!/bin/bash

# 1. .env 파일에서 환경 변수 로드
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo ".env 파일이 존재하지 않습니다."
    exit 1
fi

# 2. 기존 프로세스를 찾아서 kill
PORT=$(echo $PORT)  # 환경 변수에서 포트 가져오기

# 기존 프로세스 찾기
PIDS=$(lsof -t -i:$PORT)
if [ -n "$PIDS" ]; then
    echo "기존 프로세스(PIDs: $PIDS)를 종료합니다."
    for PID in $PIDS; do
        kill -9 $PID
        echo "종료된 프로세스 PID: $PID"
    done
else
    echo "종료할 프로세스가 없습니다."
fi


# 3. nohup.out 존재하면 삭제
if [ -f nohup.out ]; then
    echo "nohup.out 파일을 삭제합니다."
    rm nohup.out
fi

# 4. nohup을 이용하여 FastAPI 애플리케이션 실행
echo "FastAPI 애플리케이션을 nohup으로 실행합니다."
# --reload 옵션은 python -m multiprocess를 실행시켜 서브프로세스를 따로 생성시킴
nohup python -m uvicorn app:app --host $HOST --port $PORT --log-level debug > nohup.out 2>&1 &

echo "애플리케이션이 백그라운드에서 실행 중입니다."

