#!/usr/bin/env python3
# encoding: utf8
import sys
import urllib.parse

def main():
    """
    URL-encodes a string provided as a command-line argument,
    특수문자가 있는 경우는 ' ' 싱클쿼터로 묶어줘야 정상동작함.
    """
    if len(sys.argv) < 2:
        print("Usage: python urlencode.py <string_to_encode>")
        sys.exit(1)

    string_to_encode = ' '.join(sys.argv[1:])
    encoded_string = urllib.parse.quote(string_to_encode) # quote_plus() 대신 quote() 사용
    print(encoded_string)

if __name__ == "__main__":
    main()
