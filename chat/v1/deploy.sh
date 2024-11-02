#!/bin/bash
# 원격 서버에 SSH로 접속

ssh a1 << 'EOF'
# py-sniffets 디렉토리로 이동
cd ~/py-sniffets

# Git 저장소 업데이트
git pull

# chat/v1 디렉토리로 이동
cd chat/v1

# 스크립트 실행
./run.sh

# SSH 세션 종료
# exit
EOF
