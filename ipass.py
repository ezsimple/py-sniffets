#!/usr/bin/env python3
# -----------------------------------------------------------
# 16자리 영문대소문자,_,[0-9]으로 이루어진 암호 생성 프로그램
# ipass = imsi password 의 약어
# -----------------------------------------------------------

import secrets
import string
import sys

def generate_password(length=16):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(length))

# 파라미터가 주어지면 길이를 32로 설정
if len(sys.argv) > 1:
    password_length = 32
else:
    password_length = 16

password = generate_password(password_length)
print(f"임시암호 : {password}")
