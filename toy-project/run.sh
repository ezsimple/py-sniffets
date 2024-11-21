#!/bin/bash

export FLASK_APP=app
export FLASK_DEBUG=False
export APPLICATION_MODE=PRODUCTION

PATH=.:$PATH:/home/ubuntu/.pyenv/shims

[[ -f master.pid ]] && kill -9 `cat master.pid`
# --touch-reload를 이용하여 static 파일변경시 바로 반영
nohup uwsgi --ini uwsgi-toy-project.ini --touch-reload $(pwd) &
