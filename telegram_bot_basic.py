#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from LogUtil import LogUtil


class TelegramSimpleBot:
    def __init__(self):
        self.TOKEN = "5758487515:AAFfZ9fZsv7padX_6StJbn3T9zFOvW46jcc"
        self.CHAT_ID = "918743728"
        self.URL = "http://tcafe2a.com"
        self.LOGGING = LogUtil("TCAFE_ACCESS")

    def remove_tag(self, text):
        msg = "" if len(text) == 0 else "".join(text)
        return BeautifulSoup(msg, "html.parser").text

    def send_message(self, text):
        # html태그 제거(xml 구조 오류가 있어도 무시하고 파싱처리 됩니다. 단 처리속도가 다소 늦습니다.)

        msg = self.remove_tag(text)
        url = "https://api.telegram.org/bot{0}/sendMessage".format(self.TOKEN)
        params = {
            "chat_id": self.CHAT_ID,
            "text": msg,
        }
        response = requests.get(url, params=params)
        self.LOGGING.debug(text)

        # Throw an exception if Telegram API fails
        response.raise_for_status()
