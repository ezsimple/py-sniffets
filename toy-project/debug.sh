#!/bin/bash

export FLASK_APP=app
export FLASK_DEBUG=1
export APPLICATION_MODE=DEVELOPMENT

python -m flask run --host=127.0.0.1 --port 3377
