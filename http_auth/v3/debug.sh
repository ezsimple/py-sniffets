#!/bin/bash
# export PYTHONPATH=$(pwd)
# read HOST PORT < <(python -c "from core.config import print_host_port; print_host_port()")
. .env
# Hot Reload
python -m uvicorn app:app --host "$HOST" --port "$PORT" --reload
