#!/home/ubuntu/.virtualenvs/머신러닝/bin/python
# -*- coding: utf-8 -*-

# %%
import os
import json
import traceback
from io import BytesIO
from PIL import Image
import pytesseract
from playwright.sync_api import Playwright, sync_playwright, Page
from TelegramSimpleBot import TelegramSimpleBot


class AutoJobkoreaProfileUpdate:
    def __init__(self):
        self.HEADLESS = True
        self.HOST_URL = "https://www.jobkorea.co.kr"
        self.LOGIN_URL = self.HOST_URL + "/Login/Logout.asp"
        self.LOGIN_ID = "mkeasy"
        self.LOGIN_PW = "ksgi10280514!"
        self.R_NO = 918743728
        self.UPDATE_URL = self.HOST_URL + "/User/ResumeMng"
        self.STATE = "이력서 업데이트 시작"

    def handle_dialog(self, dialog):
        msg = dialog.message
        print(msg)

        bot = TelegramSimpleBot()
        bot.send_message(msg)

        dialog.dismiss()

    def ok_login(self, page):
        self.STATE = "로그인 시도"

        page.get_by_role("link", name="개인회원").click()
        page.wait_for_selector("button >> text='로그인'").click()
        page.fill('input[placeholder="아이디"]', self.LOGIN_ID)
        page.fill('input[placeholder="비밀번호"]', self.LOGIN_PW)

        # ---------------------------------------------------------------------------------
        # page.get_by_role("img", name="그림문자") .vs. page.query_selector("img[name='그림문자']") 의 차이
        # ---------------------------------------------------------------------------------
        # get_by_role: 이 메서드는 Playwright의 특정 역할(role)을 가진 요소를 검색합니다.
        # 예를 들어, "img"와 같은 역할을 가진 요소를 찾습니다.
        # 그러나 HTML 요소의 속성(attribute)을 직접적으로 지원하지 않습니다.
        # 따라서 name 속성을 사용할 수 없습니다.
        # 일반적으로 웹 표준에서 정의된 역할에 따라 요소를 찾을 때 사용됩니다.

        # query_selector: 이 메서드는 CSS 선택자를 사용하여 요소를 찾습니다.
        # 따라서 HTML 요소의 속성을 직접 지정하여 검색할 수 있습니다.
        # 예를 들어, img[name='그림문자']와 같은 선택자를 사용하여
        # "그림문자"라는 이름을 가진 이미지 태그를 찾을 수 있습니다.
        # 이 방법은 보다 유연하며, CSS 선택자의 다양한 기능을 활용하여 요소를 찾을 수 있습니다.

        # 따라서, page.query_selector("img[name='그림문자']")는 HTML 요소의 속성을 직접 지정하여 검색하는 반면,
        # page.get_by_role("img", name="그림문자")는 특정 역할에 따라 요소를 검색하는 것입니다.
        # ------------------------------------------------------------------------------------

        # captcha_element = page.get_by_role("img", name="그림문자")
        captcha_element = page.query_selector("img[name='그림문자']")
        if captcha_element:
            self.STATE = "캡챠로 인한 로그인 불가"
            raise Exception(self.STATE)

        page.get_by_role("button", name="로그인").click()

    def solve_captcha(self, page):
        captcha_image_path = "captcha_image.png"

        while True:
            self.save_captcha_image(page, captcha_image_path)

            captcha_text = self.extract_text_from_image(captcha_image_path)

            print(captcha_text)

            if (
                captcha_text.strip() != ""
                and captcha_text.isalnum()
                and captcha_text.isupper()
                and len(captcha_text) == 6
            ):
                break

            page.get_by_role("link", name="새로고침").click()

        page.get_by_placeholder("위 문자를 보이는 대로 입력해 주세요.").fill(
            captcha_text
        )
        page.get_by_role("button", name="로그인").click()

    def save_captcha_image(self, page, file_path):
        captcha_element = page.get_by_role("img", name="그림문자")

        load_state = page.wait_for_load_state("networkidle")
        page.wait_for_timeout(300)

        if load_state:
            print(load_state)
            page.get_by_role("link", name="새로고침").click()
            self.save_captcha_image(page, file_path)

        captcha_image = captcha_element.screenshot()

        image_stream = BytesIO(captcha_image)
        captcha_pil_image = Image.open(image_stream)

        with open(file_path, "wb") as file:
            file.write(captcha_image)

    def extract_text_from_image(self, image_path):
        pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

        image = Image.open(image_path)
        captcha_text = pytesseract.image_to_string(image)
        return captcha_text

    def run(self):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=self.HEADLESS)

            context = browser.new_context()
            if os.path.exists("cookies.json") and os.path.getsize("cookies.json") > 0:
                with open("cookies.json", "r") as f:
                    cookies = json.loads(f.read())
                    context.add_cookies(cookies)

            page = context.new_page()

            try:
                page.goto(self.LOGIN_URL)
                self.ok_login(page)

                with open("cookies.json", "w") as f:
                    f.write(json.dumps(context.cookies()))

                self.STATE = "이력서 최신 업데이트 시도"
                page.goto(self.UPDATE_URL)
                page.on("dialog", lambda dialog: self.handle_dialog(dialog))
                page.get_by_role("link", name="오늘 날짜로 업데이트").click()
                page.wait_for_timeout(3000)

            except Exception as e:
                print("An exception occurred:", e)

                traceback.print_exc()

                bot = TelegramSimpleBot()
                bot.send_message(f"이력서 업데이트 실패: {self.STATE}")

            finally:
                page.close()
                context.close()
                browser.close()


# %%
if __name__ == "__main__":
    clazz = AutoJobkoreaProfileUpdate()
    clazz.run()
