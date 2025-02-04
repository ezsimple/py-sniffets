#!/usr/bin/env python3

import re
import json
import os
from dotenv import load_dotenv
from playwright.sync_api import Playwright, sync_playwright, expect
import sys

# .env 파일에서 환경 변수 로드
load_dotenv()

def wait_for_loading(page):
    # 페이지 로딩이 완료될 때까지 대기하는 함수
    page.wait_for_load_state("networkidle")

def login(page):
    email = os.getenv("JOBPLANET_ID")
    password = os.getenv("JOBPLANET_PW")

    page.goto("https://www.jobplanet.co.kr/users/sign_in?_nav=gb")
    wait_for_loading(page)
    page.get_by_placeholder("이메일 주소").click()
    page.get_by_placeholder("이메일 주소").fill(email)
    page.get_by_placeholder("비밀번호 (8자리 이상)").click()
    page.get_by_placeholder("비밀번호 (8자리 이상)").fill(password)
    page.get_by_role("button", name="이메일로 로그인").click()

def run(playwright: Playwright, search_query: str) -> None:
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    login(page)

    wait_for_loading(page)

    # 검색바 클릭 및 검색어 입력
    search_bar = page.locator("#search_bar_search_query")
    search_bar.click()
    search_bar.fill(search_query)
    search_bar.press("Enter")

    wait_for_loading(page)

    # 결과 목록 요소 대기
    results_list_xpath = "/html/body/div[1]/main/div[1]/div/div/div[1]/div[2]/ul"
    try:
        # XPath를 사용하여 결과 리스트 대기
        page.locator(f"xpath={results_list_xpath}").wait_for(state="visible")

        # 기업명과 평점 추출
        company_name_xpath = "/html/body/div[1]/main/div[1]/div/div/div[1]/div[2]/ul/a[1]/div/div/div[2]/div[1]/span"
        company_rating_xpath = "/html/body/div[1]/main/div[1]/div/div/div[1]/div[2]/ul/a[1]/div/div/div[2]/div[2]/div[2]/div/div[2]/span"

        company_name = page.locator(f"xpath={company_name_xpath}").inner_text()
        company_rating = page.locator(f"xpath={company_rating_xpath}").inner_text()

        # JSON 형식으로 출력
        result = {
            "기업명": company_name,
            "기업 평점": company_rating
        }
        print(json.dumps(result, ensure_ascii=False))

    except Exception as e:
        print(f"{search_query} 검색 결과가 존재하지 않습니다.")

    page.close()
    context.close()
    browser.close()

if __name__ == "__main__":
    with sync_playwright() as playwright:
        if len(sys.argv) > 1:
            # 명령줄 인자에서 검색어 가져오기
            search_query = ' '.join(sys.argv[1:])  # 여러 단어를 공백으로 연결
            run(playwright, search_query)
        else:
            print("검색어를 입력하세요.")
