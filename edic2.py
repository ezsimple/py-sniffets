#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import sys

def search_daum_dictionary(word):
    url = f"https://dic.daum.net/search.do?q={word}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # 발음 기호 추출
    pronunciation = soup.select_one(".txt_pronounce")
    if pronunciation:
        pronunciation = pronunciation.text.strip()

    # 뜻 추출
    meanings = soup.select(".list_search > li > .txt_search")
    meanings = [meaning.text.strip() for meaning in meanings]

    return pronunciation, meanings

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: ./edic2.py 단어1 단어2 ...")
        sys.exit(1)

    for search_word in sys.argv[1:]:
        pronunciation, meanings = search_daum_dictionary(search_word)

        if pronunciation:
            print(f"단어: {search_word}, 발음 기호: {pronunciation}")

        if meanings:
            print("뜻:")
            for meaning in meanings:
                print(f"- {meaning}")

