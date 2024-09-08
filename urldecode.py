#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.parse
import sys

if len(sys.argv) <= 1:
    print('Usage : urldecode.py url')
    sys.exit(-1)

# 첫 번째 파라미터 값을 받음
encoded_value = " ".join(sys.argv[1:])
decoded_value = urllib.parse.unquote(encoded_value)
print('encoded : {0}\ndecoded : {1}'.format(encoded_value, decoded_value))
