#!/bin/bash

export FLASK_APP=app
export FLASK_DEBUG=False
export APPLICATION_MODE=PRODUCTION

PATH=.:$PATH:/home/ubuntu/.pyenv/shims

uwsgi --ini uwsgi-toy-project.ini
