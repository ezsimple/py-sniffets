#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
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
    # 뜻이 너무 많이 나와서, 다음 번역을 사용합니다.
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
            result = {
                '단어': search_word, 
                '발음': pronunciation, 
                '뜻': meanings
            }
            json_result = json.dumps(result, ensure_ascii=False, indent=2)
            print(json_result)

