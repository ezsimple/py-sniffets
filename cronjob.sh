#!/bin/bash
HOME=/home/ubuntu
PATH=.:$HOME:$HOME/.virtualenvs/강의/bin:$HOME/.local/bin:.:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
WORK_DIR=/home/ubuntu/py-sniffets
( cd $WORK_DIR; ./tcafe_session.py )
