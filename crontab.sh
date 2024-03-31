#!/bin/bash
# 10 9 * * * /home/ubuntu/py-sniffets/crontab.sh

HOME=/home/ubuntu
PATH=.:$HOME:$HOME/.virtualenvs/머신러닝/bin:$HOME/.local/bin:.:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
WORK_DIR=/home/ubuntu/py-sniffets

( cd $WORK_DIR; ./tcafe_playwright.py )
( cd $WORK_DIR; ./jobkorea_renew5.py )
( cd $WORK_DIR; ./saramin_00.py )
