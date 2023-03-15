#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import telegram
from datetime import datetime
from playwright.sync_api import Playwright, sync_playwright, expect

telegram_token = '5758487515:AAFfZ9fZsv7padX_6StJbn3T9zFOvW46jcc'
telegram_chat_id = '918743728'

def bot(txt: str) -> None:
  bot = telegram.Bot(telegram_token)
  updates = bot.getUpdates()
  chat_id = telegram_chat_id if len(updates) == 0 else updates[-1].message.chat_id

  today = datetime.today().strftime('%Y-%m-%d')
  msg = today + ' ' + '출석 완료'
  bot.sendMessage(chat_id = chat_id, text = msg)  

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    page.goto("http://tcafe2a.com/")
    page.get_by_placeholder("아이디").click()
    page.get_by_placeholder("아이디").fill("mkeasy")
    page.locator("#ol_pw").click()
    page.locator("#ol_pw").fill("dodls9gka")
    page.locator("#ol_pw").press("Enter")
    page.get_by_role("link", name="출석확인", exact=True).click()
    page.locator("#cnftjr img").click()

    # page.get_by_text("오늘 출석으로 100P 획득 하셨습니다 회원 가입 후 3007일째 이십니다.").click()
    # page.get_by_text("오늘 이미 출석 하셨습니다. 연속 출석 포인트 150P 를 위해 내일도 출석 잊지 말아 주세요. 회원 가입 후 3007일째 이십니다.").click()
    page.close()

    # ---------------------
    context.close()
    browser.close()
    bot('')


with sync_playwright() as playwright:
    run(playwright)
