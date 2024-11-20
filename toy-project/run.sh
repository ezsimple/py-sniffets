#!/bin/bash

export FLASK_APP=app
export FLASK_DEBUG=False
export APPLICATION_MODE=PRODUCTION

PATH=.:$PATH:/home/ubuntu/.pyenv/shims

nohup uwsgi --ini uwsgi-toy-project.ini &
