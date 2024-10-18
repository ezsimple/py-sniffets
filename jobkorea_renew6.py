#!/home/ubuntu/.virtualenvs/머신러닝/bin/python
import os
import json
import traceback
import logging
from playwright.sync_api import sync_playwright
from TelegramSimpleBot import TelegramSimpleBot

class AutoJobkoreaProfileUpdate:
    HEADLESS = True
    HOST_URL = "https://www.jobkorea.co.kr"
    LOGIN_URL = HOST_URL + "/Login/Logout.asp"
    LOGIN_ID = "mkeasy"
    LOGIN_PW = "ksgi10280514!"
    R_NO = 22846133
    UPDATE_URL = HOST_URL + "/User/Resume/View?rNo=" + str(R_NO)
    STATE = "이력서 업데이트 시작"

    def __init__(self):
        log_dir = "log"
        os.makedirs(log_dir, exist_ok=True)  # log 디렉토리가 없으면 생성

        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(name)s - %(filename)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(log_dir, "app.log")),  # 로그를 log/app.log 파일에 기록
                logging.StreamHandler()  # 콘솔에도 로그 출력
            ]
        )
        # 비활성화할 로거 리스트
        loggers_to_disable = [
            "starlette",
            "fastapi",
            "multipart.multipart",  # form 데이터 로깅 방지
            "urllib3"
        ]
        [logging.getLogger(logger_name).setLevel(logging.WARNING) for logger_name in loggers_to_disable]
        self.logger = logging.getLogger(__name__)

    def send_telegram(self, message=f"이력서 업데이트 실패"):
        bot = TelegramSimpleBot()
        bot.send_message(message)

    def read_alert_message(self, dialog):
        msg = dialog.message
        self.send_telegram(msg)
        # dialog.dismiss()
        self.logger.debug(msg)

    def do_login(self, page):
        self.STATE = "로그인 시도"
        page.get_by_role("link", name="개인회원").click()
        page.wait_for_selector("button >> text='로그인'").click()
        page.fill('input[name="M_ID"]', self.LOGIN_ID)
        page.fill('input[name="M_PWD"]', self.LOGIN_PW)

        # 캡차 요소가 있는지 확인
        captcha_element = page.query_selector("img[name='그림문자']")
        if captcha_element:
            self.STATE = "캡챠로 인한 로그인 불가"
            raise Exception(self.STATE)

        page.get_by_role("button", name="로그인").click()

    def page_goto(self, page, url):
        state = self.STATE
        msg = f"state: {state}, 페이지 이동: {url}"
        self.logger.debug(msg)
        page.goto(url)

    def wait_for_load_state(self, page, timeout=5000):
        page.wait_for_load_state("load", timeout=timeout)

    def close_popup(self, page):
        page.once("dialog", lambda dialog: dialog.dismiss())

    def run(self):
        with sync_playwright() as playwright:
            msg = f"HEADLESS 설정: {self.HEADLESS}"
            # print(msg)
            self.logger.debug(msg)
            browser = playwright.chromium.launch(headless=self.HEADLESS)
            context = browser.new_context()

            # 쿠키 로드
            if os.path.exists("cookies.json") and os.path.getsize("cookies.json") > 0:
                with open("cookies.json", "r") as f:
                    cookies = json.loads(f.read())
                    context.add_cookies(cookies)

            page = context.new_page()

            try:
                self.STATE = "잡코리아 로그인 시도"
                self.page_goto(page, self.LOGIN_URL)
                self.wait_for_load_state(page)
                self.close_popup(page)  # 대화상자 처리
                self.do_login(page)

                with open("cookies.json", "w") as f:
                    f.write(json.dumps(context.cookies()))

                self.STATE = "이력서 최신 업데이트 시도"
                self.page_goto(page, self.UPDATE_URL)
                self.wait_for_load_state(page)

                self.STATE = "오늘날짜로 업데이트 시도"
                page.once("dialog", self.read_alert_message) 
                page.locator('.button.button-update').click()  # 오늘날짜로 업데이트 클릭
                page.wait_for_timeout(10000)

            except Exception as e:
                msg = f'#실패# {self.STATE}, {e}' 
                # print(msg)
                self.logger.error(msg)
                traceback.print_exc()
                self.send_telegram(msg)

            finally:
                page.close()
                context.close()
                browser.close()


if __name__ == "__main__":
    app = AutoJobkoreaProfileUpdate()
    app.run()