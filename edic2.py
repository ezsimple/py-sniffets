#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# %%
import json
import requests
from bs4 import BeautifulSoup
import sys
from edic import google_translate, is_korean

def search_daum_dictionary(word):
    url = f"https://dic.daum.net/search.do?q={word}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # 발음 기호 추출
    pronunciation = soup.select_one(".txt_pronounce")
    if pronunciation:
        pronunciation = pronunciation.text.strip()

    meanings = google_translate(word)

    return pronunciation, meanings

def print_json(result):
    json_result = json.dumps(result, ensure_ascii=False, indent=2)
    print(json_result)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: ./edic2.py [단어|숙어|뜻]")
        sys.exit(-1)

    # 여러개의 파라미터를 하나의 단어로 합치기
    search_word = " ".join(sys.argv[1:])
    result = {'검색': search_word}

    if len(sys.argv) > 2 or is_korean(search_word):
        meanings = google_translate(search_word)
        if is_korean(search_word):
            result['단어'] = meanings
        else:
            result['의미'] = meanings
        print_json(result)
        sys.exit(0)

    pronunciation, meanings = search_daum_dictionary(search_word)
    result.update({'발음': pronunciation, '의미': meanings})
    print_json(result)
    sys.exit(0)