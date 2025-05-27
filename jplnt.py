import sys
import re
from playwright.sync_api import Playwright, sync_playwright, expect

JOB_PLANET="https://www.jobplanet.co.kr/job"

def run(playwright: Playwright) -> None:
    keyword = "마곡"
    if keyword is None:
        print("검색어를 입력해주세요")
        return

    keyword = keyword.replace(" ", "+")
    keyword = keyword.replace("(", "")
    keyword = keyword.replace(")", "")
    keyword = keyword.replace("주", "")
    keyword = keyword.replace(")", "")
    keyword = keyword.replace(")", "")

    # 디버깅을 위한 옵션 추가
    browser = playwright.chromium.launch(
        headless=True,  # 브라우저를 화면에 표시
        slow_mo=1000,    # 동작을 천천히
    )
    context = browser.new_context()
    page = context.new_page()
    
    # 페이지 로딩
    print("페이지 로딩 시작...")
    page.goto(JOB_PLANET)
    print("페이지 로딩 완료")
    
    # 페이지가 완전히 로드될 때까지 대기
    page.wait_for_load_state("domcontentloaded")
    print("DOM 컨텐츠 로드 완료")
    
    # 검색창이 나타날 때까지 대기
    print("검색창 대기 중...")
    # headless 모드에서는 검색창이 나타나지 않음
    page.wait_for_selector('input[type="text"]', timeout=10000)
    print("검색창 발견")
    
    # 검색창 찾기 및 입력
    search_input = page.locator('input[type="text"]').first
    search_input.fill(keyword)
    search_input.press("Enter")

    try:
        # XPath로 목록 찾기
        xpath = '//*[@id="contentsWrap"]/div[3]/div[1]/div[1]/div/div[2]/ul'
        print("검색 결과 대기 중...")
        page.wait_for_selector(f'xpath={xpath}', timeout=3000)
        print("검색 결과 발견")
        
        # 목록 요소 가져오기
        results = page.locator(f'xpath={xpath}')
        if results.count() > 0:
            print("목록을 찾았습니다!")
            # results = <Locator frame=<Frame name= url='https://www.jobplanet.co.kr/search?query=%EB%A7%88%EA%B3%A1'> selector='xpath=//*[@id="contentsWrap"]/div[3]/div[1]/div[1]/div/div[2]/ul'>
            # results.text_content() 를 \n 기준으로 파싱해서 출력
            results_list = results.text_content().split('\n')
            for result in results_list:
                print(result)
        else:
            print("목록을 찾을 수 없습니다.")
    except Exception as e:
        print('#ERROR: 검색결과를 불러오지 못했습니다.')
    finally:
        page.close()
        context.close()
        browser.close() 

if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)

