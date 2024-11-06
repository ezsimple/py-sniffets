# %%
import re
import asyncio  # asyncio 모듈을 import
from playwright.async_api import Playwright, async_playwright
import os
import asyncio
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
import sys

'''
https://www.goodreads.com/quotes/
'''
current_dir = os.path.dirname(os.path.abspath(__file__))
log_dir = os.path.join(current_dir, "log")
os.makedirs(log_dir, exist_ok=True)  # log 디렉토리가 없으면 생성

current_date = datetime.now().strftime("%Y-%m-%d")
log_file_name = f"{os.path.basename(__file__)}-{current_date}.log"
log_file_path = os.path.join(log_dir, log_file_name)
handler = TimedRotatingFileHandler(log_file_path, when="midnight", interval=1, backupCount=7)
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(filename)s - line:%(lineno)d - %(message)s'))

logging.basicConfig(
    level=logging.WARNING, # 기본 로킹레벨을 WARNING로
    handlers=[
        handler,
        logging.StreamHandler()  # 콘솔에도 로그 출력
    ]
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) # 현재 파일만 디버그 레벨로 설정


async def run(playwright: Playwright) -> None:
    # 비동기적으로 브라우저 실행
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()  # context도 비동기적으로 실행해야 합니다
    page = await context.new_page()  # page 역시 비동기적으로 생성

    href_list = []
    with open('ommit_urls.txt', 'r') as f:
        href_list = f.read().splitlines()

    MAX_ATTEMPTS = 5
    for href in href_list:
        URL = href
        href = href.split('?')[0]
        tag = href.split('/')[-1]
        for attempt in range(MAX_ATTEMPTS):  # 최대 3번 재시도
            try:
                await page.goto(URL, wait_until="networkidle", timeout=60000)
                await page.wait_for_selector('div.quote', timeout=60000)
                break  # 성공적으로 이동 시 재시도 중단
            except Exception as e:
                logger.error(f"Error occurred while navigating to {URL}: {e}")
                if attempt < MAX_ATTEMPTS - 1:  # 마지막 시도에서 실패하면 로그 출력
                    await asyncio.sleep(5)  # 5초 대기 후 재시도
                    logger.warning(f"Failed to load {URL} after {MAX_ATTEMPTS} attempts.")
                else:
                    logger.error(f"Failed to load {URL} after {MAX_ATTEMPTS} attempts.")

        if attempt >= MAX_ATTEMPTS:
            continue

        quotes = await page.query_selector_all('div.quote > div.quoteDetails > div.quoteText')
        for q in quotes:
            quote_element = await q.inner_text()
            author_element = await q.query_selector('span.authorOrTitle')
            quote = quote_element.split('―')[0].strip()
            quote = quote.replace('“', '').replace('”', '').replace('"','').replace('―','').strip().replace('<br>', '\n')
            author = await author_element.inner_text() if author_element else "Unknown"
            author = re.sub(r'\d+', '', author).replace('―', '').replace('"','').strip()
            tag = tag.replace('"', '').strip()

            with open(f'quotes-ommits.csv', 'a', encoding='utf-8') as f:
                f.write(f'"{quote}","{author}","{tag}"\n')

    # ---------------------
    await context.close()  # context도 비동기적으로 닫아야 합니다
    await browser.close()  # 브라우저 종료

# 비동기 방식으로 실행
async def main():
    async with async_playwright() as playwright:
        await run(playwright)

# main 함수를 asyncio.run()으로 호출
if __name__ == "__main__":
    asyncio.run(main())  # asyncio.run()을 통해 main()을 호출
