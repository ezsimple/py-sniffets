#!/home/ubuntu/.virtualenvs/머신러닝/bin/python
# -*- coding: utf-8 -*-

import pytesseract
from PIL import Image, ImageFilter
import cv2
import numpy as np
from io import BytesIO

from playwright.sync_api import Playwright, Browser, sync_playwright, expect, Page
from TelegramSimpleBot import TelegramSimpleBot
from playwright_stealth import stealth_sync
from playwright.sync_api import Page
import os
import json
import traceback

HEADLESS = True
HOST_URL = 'https://www.jobkorea.co.kr'
LOGIN_URL = HOST_URL + '/Login/Logout.asp'
LOGIN_ID = 'mkeasy'
LOGIN_PW = 'ksgi10280514!'
R_NO = 918743728
UPDATE_URL = HOST_URL + '/User/ResumeMng'

def handle_dialog(dialog):
    msg = dialog.message
    print(msg)

    bot = TelegramSimpleBot()
    bot.send_message(msg)

    dialog.dismiss()

def ok_login(page: Page):
    page.get_by_role("link", name="개인회원").click()
    page.wait_for_selector("button >> text='로그인'").click()
    page.fill('input[placeholder="아이디"]', LOGIN_ID)
    page.fill('input[placeholder="비밀번호"]', LOGIN_PW)
    page.get_by_role("button", name="로그인").click()

def solve_captcha(page: Page):
    # 이미지를 저장할 경로 설정
    captcha_image_path = 'captcha_image.png'

    # CAPTCHA 이미지를 저장
    while True:
        save_captcha_image(page, captcha_image_path)

        # 저장된 이미지를 로드하여 텍스트 추출
        captcha_text = extract_text_from_image(captcha_image_path)

        print(captcha_text)

         # 캡차 텍스트가 공백이 아니고, 대문자 영문과 숫자의 조합으로 6글자인 경우 반복문 탈출
        if captcha_text.strip() != "" and captcha_text.isalnum() and captcha_text.isupper() and len(captcha_text) == 6:
            break

        page.get_by_role("link", name="새로고침").click()


    page.get_by_placeholder("위 문자를 보이는 대로 입력해 주세요.").fill(captcha_text)
    page.get_by_role("button", name="로그인").click()
    # page.wait_for_timeout(2000)

    # 현재 페이지의 다이얼로그를 가져옴
    # dialog = page.wait_for_event('dialog', timeout=2000)
    if LOGIN_URL == page.url:
        page.once("dialog", lambda dialog: dialog.dismiss()) # 다이얼로그 닫기
        ok_login(page)
        solve_captcha(page)

def save_captcha_image(page: Page, file_path: str):
    captcha_element = page.get_by_role("img", name="그림문자")

    # 이미지가 로드될 때까지 대기
    load_state = page.wait_for_load_state("networkidle")
    page.wait_for_timeout(300)

    if load_state:
        print(load_state)
        page.get_by_role("link", name="새로고침").click()
        save_captcha_image(page, file_path)

    # 이미지 캡처
    captcha_image = captcha_element.screenshot()

    # 바이트로 저장된 이미지를 PIL Image 객체로 변환
    image_stream = BytesIO(captcha_image)
    captcha_pil_image = Image.open(image_stream)

    # 이미지 저장
    with open(file_path, "wb") as file:
        file.write(captcha_image)

# sudo apt install tesseract-ocr
def extract_text_from_image(image_path: str) -> str:
    # Tesseract OCR 엔진의 경로 설정
    pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

    # 이미지에서 텍스트 추출
    image = Image.open(image_path)
    captcha_text = pytesseract.image_to_string(image)
    return captcha_text

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=HEADLESS)

    context = browser.new_context()
    if os.path.exists("cookies.json") and os.path.getsize("cookies.json") > 0:  # 파일이 비어있지 않은지 확인
        with open("cookies.json", "r") as f:
            cookies = json.loads(f.read())
            context.add_cookies(cookies)

    page = context.new_page()

    try:
        # 로그인 처리
        page.goto(LOGIN_URL)

        ok_login(page)
        # solve_captcha(page) # 캡챠로 인해 로그인 못할 경우, 별도의 텔레그램 봇 발송하도록 조치한다.

        # 로그인 직후, 최신 쿠키로 업데이트 함.
        with open("cookies.json", "w") as f:
            f.write(json.dumps(context.cookies()))

        # 이력서를 최근으로 업데이트
        page.goto(UPDATE_URL)
        page.on("dialog", lambda dialog: handle_dialog(dialog))
        page.get_by_role("link", name="오늘 날짜로 업데이트").click()
        page.wait_for_timeout(3000) # 디버깅용

    except Exception as e:
        print("An exception occurred:", e)
        traceback.print_exc()

        # 예외 메시지를 텔레그램 봇으로 보냄
        bot = TelegramSimpleBot()
        bot.send_message(f"이력서 업데이트 실패: {e}\n\n{traceback.format_exc()}")

    finally:
        # page.wait_for_timeout(15000) # 디버깅용
        page.close()
        # ---------------------
        context.close()
        browser.close()

with sync_playwright() as playwright:
    # with 문으로 생성된 sync_playwright() 컨텍스트 매니저 내에서 예외를 처리하는 것은
    # 일반적으로 권장되지 않습니다. with 문은 컨텍스트 내에서 발생한 예외를 처리하지 않고
    # 바깥쪽으로 전파하기 때문입니다. 대신, run() 함수 내에서 예외를 처리하는 것이 더 적합합니다.
    run(playwright)
