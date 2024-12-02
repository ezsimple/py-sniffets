#!/bin/bash
export LANG=ko_KR.UTF-8
REPORT_DIR=/home/ubuntu/dl/접속통계
mkdir -p $REPORT_DIR

PID=$(pidof goaccess)
[[ -n "$PID" ]] && kill -9 "$PID"

goaccess /var/log/nginx/access.log --log-format=COMBINED --real-time-html -o $REPORT_DIR/report.html --daemonize
