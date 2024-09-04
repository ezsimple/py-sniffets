#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# %%
import json
import requests
from bs4 import BeautifulSoup
import sys
from edic import daum_translate, is_korean

# async 사용할 경우
# RuntimeWarning: coroutine 'search_daum_dictionary' was never awaited
# ... 
# TypeError: cannot unpack non-iterable coroutine object
# 오류 발생함.
def search_daum_dictionary(word):
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

def print_json(result):
    json_result = json.dumps(result, ensure_ascii=False, indent=2)
    print(json_result)

if __name__ == "__main__":
    # print("파라미터 갯수 : {0} {1}".format(sys.argv[0], len(sys.argv)))
    if len(sys.argv) < 2:
        print("사용법: ./edic2.py [단어|숙어|뜻]")
        sys.exit(-1)

    # 여러개의 파라미터를 하나의 단어로 합치기
    search_word = " ".join(sys.argv[1:])

    # 파라미터 갯수가 2초과할 경우
    if len(sys.argv) > 2:
        meanings = daum_translate(search_word)
        result = {
            '숙어': search_word,
            '뜻': meanings
        }
        print_json(result)
        sys.exit(0)

    if is_korean(search_word):
        meanings = daum_translate(search_word)
        result = {
            '한글': search_word,
            '영어': meanings
        }
        print_json(result)
        sys.exit(0)

    # 영문단어 검색 (하나의 단어 검색시도시)
    pronunciation, meanings = search_daum_dictionary(search_word)
    result = {
        '단어': search_word, 
        '발음': pronunciation, 
        '뜻': meanings
    }
    print_json(result)
    

    # loop = asyncio.get_event_loop()
    # for search_word in sys.argv[1:]:
    #     pronunciation, meanings = loop.run_until_complete(search_daum_dictionary(search_word))

    #     if search_word or pronunciation or meanings:
    #         result = {
    #             '단어': search_word, 
    #             '발음': pronunciation, 
    #             '뜻': meanings
    #         }
    #         json_result = json.dumps(result, ensure_ascii=False, indent=2)
    #         print(json_result)

