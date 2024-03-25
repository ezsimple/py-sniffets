#!/usr/bin/env python3
# -*- coding: utf8 -*-

# https://www.inflearn.com/questions/737370/%ED%85%94%EB%A0%88%EA%B7%B8%EB%9E%A8-%EB%B4%87-%EB%AA%85%EB%A0%B9%EC%96%B4-%EC%98%A4%EB%A5%98-%EC%A7%88%EB%AC%B8%EB%93%9C%EB%A6%BD%EB%8B%88%EB%8B%A4
# https://github.com/python-telegram-bot/python-telegram-bot/wiki/Code-snippets

import telegram
import time
import datetime

import asyncio

TOKEN = "5758487515:AAFfZ9fZsv7padX_6StJbn3T9zFOvW46jcc"
CHAT_ID = "918743728"


async def main(msg):  # 실행시킬 함수명 임의지정
    token = TOKEN
    bot = telegram.Bot(token=TOKEN)
    # await bot.send_message(CHAT_ID, msg)
    # https://github.com/python-telegram-bot/python-telegram-bot/wiki/Code-snippets
    await bot.send_message(chat_id=CHAT_ID, text=msg)


# yyyy-mm-dd now time format
today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
asyncio.run(main("{} 출석완료".format(today)))  # 봇 실행하는 코드
