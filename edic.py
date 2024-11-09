#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import re
import sys
import requests
import urllib3
import json
import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# source from https://github.com/monologg/kakaotrans
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
BASE_URL = "https://translate.kakao.com/translator/translate.json"
LANGUAGES = {
    "kr": "korean",
    "en": "english",
    "jp": "japanese",
    "cn": "chinse",
    "vi": "vietnamese",
    "id": "indonesian",
    "ar": "arabic",
    "bn": "bengali",
    "de": "german",
    "es": "spanish",
    "fr": "french",
    "hi": "hindi",
    "it": "italian",
    "ms": "malay",
    "nl": "dutch",
}


class DaumTranslator(object):
    """
    Kakao Translate ajax API implemenation class
    You have to create an instance of Translator to use this API
    """

    def __init__(self, service_url=None, user_agent=DEFAULT_USER_AGENT):

        self.service_url = service_url or BASE_URL

        self.headers = {
            "Host": "translate.kakao.com",
            "Connection": "keep-alive",
            "Accept": "application/json; charset=UTF-8",
            "Origin": "https://translate.kakao.com",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": user_agent,
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": "https://translate.kakao.com/",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7,la;q=0.6",
        }

    def translate(
        self,
        query,
        src="en",
        tgt="kr",
        separate_lines=False,
        save_as_file=False,
        file_name=None,
    ):
        """
        Translate text from source language to target langauge
        :param query: The source text to be translated
        :param src: Source language. You can set as 'auto' for auto detecting the source language.
        :param tgt: Target Language
        :param separate_lines: If this is set as True, this function will return the list of translated sentences
        :param save_as_file: Whether save the translated result as file or not
        :param file_name: File name for saving the result.
        :return: Translated Text
                 If separate_line==False, return the translated result in one sentence
                 If separate_line==True, return the list of multiple translated sentences
        Basic usage:
            >>> from kakaotrans import Translator
            >>> translator = Translator()
            >>> translator.translate("Try your best rather than be the best.")
        """
        # To replace multiple whitespace to single whitespace
        # This helps the translator to understand the query and split the sentences more clearly
        query = " ".join(query.strip().split())

        results = is_korean(query)
        if results:
            src = "kr"
            tgt = "en"

        # Assert language code
        if src != "auto" and src not in LANGUAGES:
            raise ValueError("Invalid source language")
        if tgt not in LANGUAGES:
            raise ValueError("Invalid target language")
        if src == tgt:
            raise ValueError("Source language and Target language cannot be same")

        # Send the POST request
        params = {"queryLanguage": src, "resultLanguage": tgt, "q": query}
        response = requests.post(
            self.service_url, headers=self.headers, data=params, verify=False
        )

        # Check whether the status code is 200
        if response.status_code != 200:
            raise Exception("Response Error")

        translated_lines = response.json()["result"]["output"][0]

        # Save the result as file
        if save_as_file and not file_name:
            raise ValueError(
                "You must specified the filename if you want to save the result as file."
            )

        if save_as_file:
            with open(file_name, "w", encoding="utf-8") as f:
                for line in translated_lines:
                    f.write(line + "\n")

        if separate_lines:
            return translated_lines
        else:
            return " ".join(translated_lines)


def is_korean(query):
    pattern = re.compile(r"[ㄱ-ㅣ가-힣]")
    results = re.findall(pattern, query)
    return results


def daum_translate(target_str):
	translator = DaumTranslator()
	return (translator.translate(target_str))

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

    meanings = daum_translate(word)

    return pronunciation, meanings


def print_json(result):
    json_result = json.dumps(result, ensure_ascii=False, indent=2)
    print(json_result)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: ./edic.py [단어|숙어|한글]")
        sys.exit(-1)

    # 여러개의 파라미터를 하나의 단어로 합치기
    search_word = " ".join(sys.argv[1:])
    result = {'검색': search_word}

    if len(sys.argv) > 2 or is_korean(search_word):
        meanings = daum_translate(search_word)
        result['의미'] = meanings
        print_json(result)
        sys.exit(0)

    pronunciation, meanings = search_daum_dictionary(search_word)
    result.update({'발음': pronunciation, '의미': meanings})
    print_json(result)
    sys.exit(0)