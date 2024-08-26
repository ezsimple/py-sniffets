#!/home/ubuntu/.virtualenvs/머신러닝/bin/python
# -*- coding: utf-8 -*-

# %%
from playwright.sync_api import Playwright, sync_playwright, Page
import requests
from LogUtil import LogUtil
from lxml import html
import random

TOKEN = "5758487515:AAFfZ9fZsv7padX_6StJbn3T9zFOvW46jcc"
CHAT_ID = "918743728"
URL = "http://tcafe2a.com"
LOGGING = LogUtil("TCAFE_ACCESS")


def send_message(text):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    params = {
        "chat_id": CHAT_ID,
        "text": text,
    }
    resp = requests.get(url, params=params)
    LOGGING.debug(text)

    # Throw an exception if Telegram API fails
    resp.raise_for_status()

def simulate_human_behavior() -> int:
    """
    https://www.zenrows.com/blog/playwright-cloudflare-bypass#simulate-human-behavior
    이 코드에서는 random.random()을 사용하여 0과 1 사이의 난수를 생성한 후, 
    이를 2000으로 곱하고 1000을 더하여 범위를 1000에서 3000으로 설정합니다. 
    """
    return int(random.random() * 2000 + 1000)

def close_notify(page: Page):
    try:
        close_button = page.wait_for_selector('button >> text="닫기"', timeout=1000)
        close_button.click()
    except Exception as e:
        print(e)
        pass


# async def report():
#     today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     msg = "{} 출석완료".format(today)
#     bot = telegram.Bot(token = TOKEN)
#     await bot.send_message(CHAT_ID, msg)


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    STATE = "티카페 사이트 접근"
    try:
        page.goto(URL)

        # close_notify(page)

        page.locator("#ol_id").click()
        page.locator("#ol_id").fill("mkeasy")
        page.locator("#ol_pw").click()
        page.locator("#ol_pw").fill("dodls9gka")
        page.locator("#ol_pw").press("Enter")
        page.get_by_role("link", name="출석확인", exact=True).click()
        page.locator("#cnftjr img").click()
        # page.wait_for_timeout(1000)


	# XPath를 사용해 특정 요소가 로드될 때까지 대기
        xpath = '//*[@id="thema_wrapper"]/div/div[3]/div/div/div[1]/div/div[2]/div[1]'
        element_handle = page.wait_for_selector(xpath)
        # print(element_handle)

        if element_handle:
            # 페이지 HTML 가져오기
            html_content = page.content()

            # lxml을 이용해 HTML 파싱
            tree = html.fromstring(html_content)

            # XPath를 사용해 특정 요소의 텍스트 추출
            elements = tree.xpath(xpath)
            
            if elements:
                text = elements[0].text_content()
                send_message(text)
                return

            text = f"#ERROR# 출첵메세지 없음: {URL}"
            send_message(text)
            return
            
        text = f"#ERROR# tcafe2a 출책 안됨 : {URL}"
        send_message(text)
        return


        # 출첵확인
        #html = page.content()
        #txt = re.compile(r"출석.*주세요|출석.*획득").findall(html)
        #msg = "출석 확인 필요합니다." if len(txt) == 0 else "".join(txt)
        #msg = BeautifulSoup(
        #    msg, "html.parser"
        #).text  # html태그 제거(xml 구조 오류가 있어도 무시하고 파싱처리 됩니다. 단 처리속도가 다소 늦습니다.)
        #send_message(msg)

    except Exception as e:
        text = f"#ERROR# tcafe2a 출책 실패: {URL}"
        send_message(text)
        pass

    finally:
        page.close()
        # ---------------------
        context.close()
        browser.close()


# %%
with sync_playwright() as playwright:
    run(playwright)
