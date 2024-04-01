#!/home/ubuntu/.virtualenvs/머신러닝/bin/python
# -*- coding: utf-8 -*-

from playwright.sync_api import sync_playwright
from TelegramSimpleBot import TelegramSimpleBot


class AutoSaraminUpdateResume:
    HEADLESS = True
    LOGIN_URL = "https://www.saramin.co.kr/zf_user/auth?ut=p"
    LOGIN_ID = "ezsimple"
    LOGIN_PW = "dbslgusl2Qh!"
    WORK_URL = "https://www.saramin.co.kr/zf_user/resume/resume-manage"

    def __init__(self):
        self.bot = TelegramSimpleBot()

    def handle_dialog(self, dialog):
        msg = dialog.message
        print(msg)
        dialog.accept()  # confirm 창일 때 사용
        self.bot.send_message(msg)

        # dialog.dismiss() # alert 창의 경우 사용

    def run(self):
        STATE = "사람인 업데이트 시작"

        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=self.HEADLESS)
                context = browser.new_context()
                page = context.new_page()

                page.goto(self.LOGIN_URL)
                STATE = "사람인 로그인 시도"
                page.get_by_label("아이디", exact=True).click()
                page.get_by_label("아이디", exact=True).fill(self.LOGIN_ID)
                page.get_by_label("비밀번호").click()
                page.get_by_label("비밀번호").fill(self.LOGIN_PW)
                page.get_by_role("button", name="로그인").click()

                STATE = "사람인 로그인 성공"
                wait_point = page.wait_for_selector(
                    'button >> text="나의 알림"', timeout=1000
                )

                STATE = "오늘 날짜로 업데이트 시도"
                page.goto(self.WORK_URL)
                wait_point = page.wait_for_selector(
                    'button >> text="오늘 날짜로 업데이트"', timeout=1000
                )
                page.on("dialog", lambda dialog: self.handle_dialog(dialog))
                page.get_by_role("button", name="오늘 날짜로 업데이트").click()

                page.wait_for_timeout(3000)

        except Exception as e:
            self.bot.send_message(f"사람인 이력서 업데이트 실패: {STATE}")

        finally:
            page.close()
            context.close()
            browser.close()


if __name__ == "__main__":
    clazz = AutoSaraminUpdateResume()
    clazz.run()
