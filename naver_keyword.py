#!/usr/bin/env python3
# coding: utf-8
import json
import asyncio
import urllib.parse
import datetime
import os
import sys
from dotenv import load_dotenv
import yaml

# 특정키워드로 오늘 발행되는 포스팅 예상갯수(A) = 100 / (오늘날짜 - 특정키워드로 발행된 100번째 포스팅이 올라온 날짜)
# 포스팅이란? A 값이 낮을수록 좋은 키워드 입니다.

# 현재 파일의 디렉토리 경로 가져오기
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, '.env')

# .env 파일 로드
load_dotenv(dotenv_path=env_path)

# .env 네이버 API 아이디/비번 발행
client_id = os.getenv("NAVER_BLOG_SEARCH_CLIENT_ID")
client_secret = os.getenv("NAVER_BLOG_SEARCH_CLIENT_SECRET")

if not client_id or not client_secret:
    print("클라이언트 아이디 또는 시크릿이 .env 파일에 설정되어 있지 않습니다.")
    print(f"현재 디렉토리: {current_dir}")
    print(f".env 파일 경로: {env_path}")
    sys.exit(1)

def decode_html_entities(text):
    """HTML 특수 문자를 디코딩하는 함수"""
    import html
    return html.unescape(text)

from playwright.async_api import async_playwright

async def main(keyword):
    # 3. 네이버 검색 API를 해당키워드의 최근 100개의 발행개수를 확인한다.
    encText = urllib.parse.quote(keyword)
    display = 100
    sort = 'date'

    url = f"https://openapi.naver.com/v1/search/blog?query={encText}&display={display}&sort={sort}"

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()

        # API 요청
        response = await page.request.get(url, headers={
            "X-Naver-Client-Id": client_id,
            "X-Naver-Client-Secret": client_secret
        })
        
        if response.status == 200:
            response_body = await response.json()

            # YAML 결과 출력
            items_list = []
            for item in response_body.get("items", []):
                title = decode_html_entities(item["title"])
                description = decode_html_entities(item["description"])

                # 각 항목을 딕셔너리로 구성
                # Python 3.7 이상에서는 일반 딕셔너리도 삽입 순서를 유지하므로
                # 별도로 OrderedDict를 사용할 필요가 없습니다.
                item_dict = {
                    "제목": title,
                    "링크": item['link'],
                    "설명": description,
                    "블로거 이름": item['bloggername'],
                    "포스팅 날짜": item['postdate']
                }
                items_list.append(item_dict)

            # YAML 형식으로 출력 ,dict 삽입순서 유지를 위해 sort_keys=False
            print(yaml.dump(items_list, allow_unicode=True, default_flow_style=False, sort_keys=False))
        else:
            print("Error Code:", response.status)
        
        await browser.close()

    # 4. 해당 키워드의 포스팅일자와 총 발행량을 체크한다.
    posting_total = 100
    print("총 발행량:", posting_total)

    if "items" in response_body and response_body["items"]:
        last_posting = response_body["items"][-1]
        print("마지막 포스팅 생성날짜:", last_posting["postdate"])

        # 오늘 날짜 확인
        today = datetime.datetime.today()
        print("오늘 날짜:", today)

        # 마지막 포스팅 생성날짜 datetime 변환
        last_year = int(last_posting["postdate"][:4])
        last_month = int(last_posting["postdate"][4:6])
        last_day = int(last_posting["postdate"][6:])
        last = datetime.datetime(last_year, last_month, last_day)

        # 마지막 포스팅일자 - 오늘 날짜 계산
        date_difference = today - last
        print("일수 차이:", date_difference.days)

        # 5. 오늘 글을 올렸을 때의 경쟁률을 알아본다.
        daily_average = posting_total / date_difference.days if date_difference.days > 0 else posting_total
        print("오늘 글을 올렸을 때의 경쟁률 (낮을수록 좋음)")
        print("하루 평균 발행량(경쟁률):", daily_average)
        print(f"검색 키워드:{keyword}")
        # print(f"검색 URL:{url}")
    else:
        print("No postings found.")

if __name__ == "__main__":
    # 전체 경로에서 파일명만 가져오기
    prog_name = os.path.basename(sys.argv[0])
    if len(sys.argv) > 1:
        keyword = ' '.join(sys.argv[1:])  # argv[1:]를 통해 키워드를 가져옴
        asyncio.run(main(keyword))
    else:
        print(f"키워드를 입력하세요. 사용법: python {prog_name} [키워드]")

