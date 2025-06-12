#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
import random
import asyncio
from playwright.async_api import async_playwright, TimeoutError
import json

async def close_popup_with_esc(page, attempts=3):
    """ESC 키를 사용하여 팝업 닫기 시도"""
    print("ESC 키로 팝업 닫기 시도 중...")
    for i in range(attempts):
        try:
            # 키보드 이벤트를 직접 발생시킴
            await page.evaluate("""
                document.dispatchEvent(new KeyboardEvent('keydown', {
                    key: 'Escape',
                    code: 'Escape',
                    keyCode: 27,
                    which: 27,
                    bubbles: true
                }));
            """)
            print(f"ESC 키 입력 {i+1}회")
            await asyncio.sleep(1)
        except Exception as e:
            print(f"ESC 키 입력 중 오류: {str(e)}")
            continue

async def wait_for_page_load(page, timeout=10):
    """페이지 로딩이 완료될 때까지 대기"""
    print("페이지 로딩 완료 대기 중...")
    try:
        # DOM이 안정화될 때까지 대기
        await page.wait_for_load_state('domcontentloaded', timeout=timeout * 1000)
        print("페이지 로딩 완료")
        return True
    except Exception as e:
        print(f"페이지 로딩 대기 중 오류: {str(e)}")
        return False

async def search_companies(query):
    """잡플래닛에서 기업 검색"""
    try:
        async with async_playwright() as p:
            # 브라우저 설정
            browser = await p.chromium.launch(
                headless=True,
                args=['--disable-dev-shm-usage']
            )
            
            # 컨텍스트 생성
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
            )
            
            # 페이지 생성
            page = await context.new_page()
            
            # 타임아웃 설정
            page.set_default_timeout(10000)  # 10초로 감소
            
            # URL 설정
            url = f"https://www.jobplanet.co.kr/search?query={query}"
            print(f"요청 URL: {url}")
            
            # 페이지 로드
            try:
                # 페이지 로드 시도
                response = await page.goto(url, wait_until='domcontentloaded', timeout=10000)
                await asyncio.sleep(3)  # 팝업 닫힘 대기
                if not response:
                    print("페이지 로드 실패")
                    await browser.close()
                    return []
                
                # 페이지 로딩 완료 대기
                if not await wait_for_page_load(page):
                    print("페이지 로딩 시간 초과")
                    await browser.close()
                    return []
                
                # ESC 키로 팝업 닫기 시도
                await close_popup_with_esc(page)
                
                # 검색 결과 확인
                print("검색 결과 확인 중...")
                company_elements = await page.query_selector_all('xpath=/html/body/div[1]/main/div/div[3]/div[1]/div[1]/div/div[2]/ul/a')
                if not company_elements:
                    print("검색 결과를 찾을 수 없습니다.")
                    await browser.close()
                    return []
                
                print(f"발견된 회사 수: {len(company_elements)}")
                
                # 스크롤 다운
                # print("스크롤 다운 중...")
                # for i in range(5):
                #     await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                #     await asyncio.sleep(2)
                
                # 회사 정보 추출
                companies = []
                
                for element in company_elements:
                    try:
                        # 회사명 찾기 (정확한 XPath 사용)
                        name_element = await element.query_selector('xpath=./div/div[1]/div[2]/div/h4')
                        if not name_element:
                            print("회사명 요소를 찾을 수 없음")
                            continue
                            
                        name = await name_element.inner_text()
                        name = name.strip()
                        if not name or len(name) < 2:
                            print(f"유효하지 않은 회사명: {name}")
                            continue
                        
                        # 평점 찾기 (정확한 XPath 사용)
                        rating = "정보 없음"
                        rating_element = await element.query_selector('xpath=./div/div[1]/div[2]/div/div/div[1]/span[2]')
                        if rating_element:
                            rating_text = await rating_element.inner_text()
                            rating_text = rating_text.strip()
                            print(f"평점 텍스트: {rating_text}")
                            # 숫자만 추출
                            import re
                            rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                            if rating_match:
                                rating = rating_match.group(1)
                        
                        # 회사명에 특수문자나 숫자가 포함된 경우 제외
                        if re.search(r'[0-9+\-]', name):
                            print(f"특수문자/숫자 포함된 회사명 제외: {name}")
                            continue
                        
                        # 중복 제거
                        if not any(c['name'] == name for c in companies):
                            companies.append({
                                'name': name,
                                'rating': rating
                            })
                            print(f"회사 정보 추출 성공: {name} - {rating}")
                        
                    except Exception as e:
                        print(f"회사 정보 추출 중 오류: {str(e)}")
                        continue
                
                # 브라우저 종료
                await browser.close()
                return companies
                
            except TimeoutError as e:
                print(f"페이지 로딩 타임아웃: {str(e)}")
                await browser.close()
                return []
            
    except Exception as e:
        print(f"오류가 발생했습니다: {str(e)}")
        return []

def main():
    """메인 함수"""
    if len(sys.argv) != 2:
        print("사용법: python jpl.py <검색어>")
        sys.exit(1)
    
    query = sys.argv[1]
    print(f"검색어: {query}")
    
    # 비동기 함수 실행
    companies = asyncio.run(search_companies(query))
    
    if not companies:
        print("검색 결과가 없습니다.")
        sys.exit(1)
    
    # 결과 출력
    print("\n검색 결과:")
    for company in companies:
        print(f"회사명: {company['name']}")
        print(f"평점: {company['rating']}")
        print("-" * 50)
    
    # JSON 파일로 저장
    if len(companies) > 0:
        output_file = f"/tmp/jobplanet_{query}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(companies, f, ensure_ascii=False, indent=2)
        print(f"\n결과가 {output_file}에 저장되었습니다.")
        
        # PostgreSQL에 저장
        try:
            import subprocess
            subprocess.run(['python', 'save_to_db.py', output_file], check=True)
        except subprocess.CalledProcessError as e:
            print(f"데이터베이스 저장 중 오류: {str(e)}")
        except Exception as e:
            print(f"데이터베이스 저장 중 오류: {str(e)}")

if __name__ == "__main__":
    main()