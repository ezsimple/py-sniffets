#!/bin/bash
# Here Document << 'EOF'
# 원격 서버에 SSH로 접속

ssh a1 << 'EOF'
# 최신버전으로 업데이트
(cd ~/py-sniffets; git pull)
# 재시동
(cd ~/py-sniffets/chat/v1; ./run.sh)
# SSH 세션 종료
exit
EOF
