#!/bin/bash
# Hot Reload
python -m uvicorn app:app --host 127.0.0.1 --port 3333 --reload
