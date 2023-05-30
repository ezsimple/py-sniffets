#!/usr/bin/env python
# -*- coding: utf-8 -*-

from playwright.sync_api import Playwright, sync_playwright, expect

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.jobkorea.co.kr/Login/Login_Tot.asp")
    page.get_by_label("아이디").click()
    page.get_by_label("아이디").fill("mkeasy")
    page.get_by_label("비밀번호").click()
    page.get_by_label("비밀번호").fill("ksgi10280514!")
    page.get_by_role("button", name="로그인").click()
    page.get_by_role("link", name="이력서 관리").click()
    storage = context.storage_state(path="state.json")
    with page.expect_popup() as page1_info:
        page.get_by_role("link", name="Springboot/ Python/ React ( MSA/ 개발 총괄 )").click()
    page1 = page1_info.value
    page1.once("dialog", lambda dialog: dialog.dismiss())
    page1.get_by_role("button", name="오늘날짜로 업데이트").click()
    page1.close()
    page.close()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
