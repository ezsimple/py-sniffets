#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import requests
from bs4 import BeautifulSoup
import sys
from edic import daum_translate

async def search_daum_dictionary(word):
    url = f"https://dic.daum.net/search.do?q={word}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # 발음 기호 추출
    pronunciation = soup.select_one(".txt_pronounce")
    if pronunciation:
        pronunciation = pronunciation.text.strip()

    # 뜻 추출
    # meanings = soup.select(".list_search > li > .txt_search")
    # meanings = [meaning.text.strip() for meaning in meanings]
    # 주의 : await 를 사용하면 동기화 처리가 되지 않음
    meanings = daum_translate(word)

    return pronunciation, meanings

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: ./edic2.py 단어1 단어2 ...")
        sys.exit(1)

    loop = asyncio.get_event_loop()
    for search_word in sys.argv[1:]:
        pronunciation, meanings = loop.run_until_complete(search_daum_dictionary(search_word))

        if search_word or pronunciation or meanings:
            print(f"'단어': {search_word}, '발음기호': {pronunciation}, '뜻':{meanings}")

