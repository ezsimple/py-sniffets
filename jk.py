#!/usr/bin/env python

# %%
from playwright.sync_api import Playwright, sync_playwright, expect
from telegram_bot_basic import TelegramSimpleBot


# page1.on("dialog", lambda dialog: print(dialog.message))
def handle_dialog(dialog):
    msg = dialog.message
    print(msg)

    bot = TelegramSimpleBot()
    bot.send_message(msg)

    # print("{}, {}".format(dialog.type, dialog.message))
    # assert dialog.type == "beforeunload"
    dialog.dismiss()


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.jobkorea.co.kr/Login/Login_Tot.asp")
    page.get_by_label("아이디").click()
    page.get_by_label("아이디").fill("mkeasy")
    page.get_by_label("비밀번호").click()
    page.get_by_label("비밀번호").fill("ksgi10280514!")
    page.get_by_role("button", name="로그인").click()
    page.get_by_role("link", name="이력서 관리").click()
    with page.expect_popup() as page1_info:
        page.get_by_role(
            "link", name="Springboot/ Python/ React ( MSA/ 개발 총괄 )"
        ).click()
    page1 = page1_info.value

    page1.on("dialog", lambda dialog: handle_dialog(dialog))
    page1.get_by_role("button", name="오늘날짜로 업데이트").click()

    page1.wait_for_timeout(3000)
    page1.close(run_before_unload=True)

    page.wait_for_timeout(1000)
    page.close()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
