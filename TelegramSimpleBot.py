#!/home/ubuntu/.virtualenvs/머신러닝/bin/python
# -*- coding: utf-8 -*-

# -------------------------------------------------
# 사용법 
# -------------------------------------------------
# from TelegramSimpleBot import TelegramSimpleBot
# bot = TelegramSimpleBot()
# bot.send_message("이것은 테스트 메시지입니다.")

import requests
from LogUtil import LogUtil

class TelegramSimpleBot:
    def __init__(self):
        TOKEN = '5758487515:AAFfZ9fZsv7padX_6StJbn3T9zFOvW46jcc'
        CHAT_ID = '918743728'
        self._token = TOKEN
        self._chat_id = CHAT_ID
        self._logging = LogUtil('TELEGRAM_BOT')

    def send_message(self, text):
        url = f"https://api.telegram.org/bot{self._token}/sendMessage"
        params = {
            "chat_id": self._chat_id,
            "text": text,
        }

        resp = requests.get(url, params=params)
        self._logging.debug(text)

        # Throw an exception if Telegram API fails
        resp.raise_for_status()

if __name__ == "__main__":
    # 예시로 사용할 토큰과 챗 ID

    # TelegramSimpleBot 클래스 인스턴스 생성
    bot = TelegramSimpleBot()

    # 테스트 메시지 전송
    bot.send_message("텔레그램 봇 메시지입니다.")

