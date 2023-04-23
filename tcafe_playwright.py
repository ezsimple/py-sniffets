#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import telegram
from datetime import datetime
from playwright.sync_api import Playwright, sync_playwright, expect
import asyncio
import requests
import re
from bs4 import BeautifulSoup

TOKEN = '5758487515:AAFfZ9fZsv7padX_6StJbn3T9zFOvW46jcc'
CHAT_ID = '918743728'
URL = "http://tcafe2a.com"

def send_message(text):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    params = {
      "chat_id": CHAT_ID,
      "text": text,
    }
    resp = requests.get(url, params=params)

    # Throw an exception if Telegram API fails
    resp.raise_for_status()

# async def report():
#     today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     msg = "{} 출석완료".format(today)
#     bot = telegram.Bot(token = TOKEN)
#     await bot.send_message(CHAT_ID, msg)

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    page.goto(URL)
    page.locator("#ol_id").click()
    page.locator("#ol_id").fill("mkeasy")
    page.locator("#ol_pw").click()
    page.locator("#ol_pw").fill("dodls9gka")
    page.locator("#ol_pw").press("Enter")
    page.get_by_role("link", name="출석확인", exact=True).click()
    page.locator("#cnftjr img").click()

    # page.goto(URL + "/attendance/selfattend2_p.php")
    # html = page.content()
    # print(html)

    # txt = re.compile(r'출석.*주세요|출석.*획득').findall(html)
    # msg = '출석 확인 필요합니다.' if len(txt) == 0 else ''.join(txt)
    # msg = BeautifulSoup(msg, "html.parser").text # html태그 제거(xml 구조 오류가 있어도 무시하고 파싱처리 됩니다. 단 처리속도가 다소 늦습니다.)

    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = "{} 출석완료".format(today)
    send_message(msg)

    page.close()


    # ---------------------
    context.close()
    browser.close()

    # today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # msg = "{} 출석완료".format(today)
    # send_message(msg)

with sync_playwright() as playwright:
  run(playwright)
