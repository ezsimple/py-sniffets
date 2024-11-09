#!/usr/bin/env python3
# -----------------------------------------------------------
# 16자리 영문대소문자,_,[0-9]으로 이루어진 암호 생성 프로그램
# ipass = imsi password 의 약어
# -----------------------------------------------------------

import secrets
import string

def generate_password(length=16):
		# special_characters = "!@#$%^&*()_+-=[]{}|;:'\",.<>?/"
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(length))

password = generate_password()
print(f"임시암호 : {password}")
