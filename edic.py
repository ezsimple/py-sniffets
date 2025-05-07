#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import requests
from bs4 import BeautifulSoup
import sys
from deep_translator import GoogleTranslator
import re

def is_korean(query):
    pattern = re.compile(r"[ㄱ-ㅣ가-힣]")
    results = re.findall(pattern, query)
    return results

def google_translate(target_str):
    if is_korean(target_str):
        translator = GoogleTranslator(source='ko', target='en')
        return translator.translate(target_str)

    translator = GoogleTranslator(source='en', target='ko')
    return translator.translate(target_str)

def search_daum_dictionary(word):
    url = f"https://dic.daum.net/search.do?q={word}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # 발음 기호 추출
    pronunciation = soup.select_one(".txt_pronounce")
    if pronunciation:
        pronunciation = pronunciation.text.strip()

    # Google Translator를 사용하여 뜻 번역
    meanings = google_translate(word)

    return pronunciation, meanings

def print_json(data):
    print(json.dumps(data, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: ./edic.py [단어|숙어|뜻]")
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