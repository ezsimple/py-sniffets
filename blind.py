#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import re
import subprocess
import time
import random
import asyncio
from playwright.async_api import async_playwright, TimeoutError
import json
from tqdm import tqdm
import groq
from typing import List, Dict
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

async def pause():
    """디버깅을 위한 일시 정지"""
    print("\n#DEBUG# 일시 정지 중... (계속하려면 Enter 키를 누르세요)")
    input()

async def close_popup_with_esc(page, attempts=3):
    """ESC 키를 사용하여 팝업 닫기 시도"""
    # print("ESC 키로 팝업 닫기 시도 중...")
    for i in tqdm(range(attempts), desc="팝업 닫기"):
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
            await asyncio.sleep(0.3)
        except Exception as e:
            print(f"#ERROR# ESC 키 입력 중 오류: {str(e)}")
            continue

async def wait_for_page_load(page, timeout=10):
    """페이지 로딩이 완료될 때까지 대기"""
    # print("페이지 로딩 완료 대기 중...")
    try:
        # DOM이 안정화될 때까지 대기
        await page.wait_for_load_state('domcontentloaded', timeout=timeout * 1000)
        # print("페이지 로딩 완료")
        return True
    except Exception as e:
        print(f"#ERROR# 페이지 로딩 대기 중 오류: {str(e)}")
        return False

async def summarize_reviews(reviews: List[str], company_name: str) -> str:
    """GROQ를 사용하여 리뷰 요약"""
    try:
        # GROQ API 키 확인
        api_key = os.getenv("GRQ_API_KEY")
        if not api_key:
            print("#ERROR# GRQ_API_KEY 환경 변수가 설정되지 않았습니다.")
            return "리뷰 요약을 생성할 수 없습니다. (API 키 누락)"
        
        print(f"[DEBUG] API 키 확인 완료: {api_key[:5]}...")
        
        # GROQ 모델 확인
        model = os.getenv("GRQ_MODEL", "모델이 없습니다. 선택하세요.")  # 기본값 설정
        print(f"[DEBUG] 사용할 모델: {model}")
        
        # GROQ 클라이언트 초기화
        client = groq.Groq(api_key=api_key)
        print("[DEBUG] GROQ 클라이언트 초기화 완료")
        
        # 리뷰 텍스트 결합
        reviews_text = "\n".join(reviews)
        print(f"[DEBUG] 리뷰 텍스트 길이: {len(reviews_text)} 문자")
        
        # 프롬프트 생성
        prompt = f"""
        다음은 {company_name}에 대한 직원 리뷰입니다. 
        이 리뷰들을 분석하여 다음 항목별로 요약해주세요:
        1. 긍정적인 평가
        2. 부정적인 평가
        3. 개선이 필요한 부분
        4. 전반적인 평가

        리뷰:
        {reviews_text}
        """
        print("[DEBUG] 프롬프트 생성 완료")
        
        # GROQ API 호출
        print("[DEBUG] GROQ API 호출 시작...")
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "당신은 회사 리뷰를 분석하고 요약하는 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        print("[DEBUG] GROQ API 호출 완료")
        
        summary = completion.choices[0].message.content
        print(f"[DEBUG] 요약 생성 완료 (길이: {len(summary)} 문자)")
        return summary
        
    except groq.GroqError as e:
        print(f"#ERROR# GROQ API 오류 발생: {str(e)}")
        print(f"#ERROR# 오류 상세: {e.__class__.__name__}")
        return "리뷰 요약을 생성할 수 없습니다. (GROQ API 오류)"
    except Exception as e:
        print(f"#ERROR# 리뷰 요약 중 오류 발생: {str(e)}")
        print(f"#ERROR# 오류 타입: {e.__class__.__name__}")
        print(f"#ERROR# 오류 상세: {e.__dict__}")
        return "리뷰 요약을 생성할 수 없습니다."

async def search_companies(query):
    """잡플래닛에서 기업 검색"""
    try:
        async with async_playwright() as p:
            # 브라우저 설정
            browser = await p.chromium.launch(
                headless=False,
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
            search_url = "https://www.teamblind.com/kr/company"
            print(f"[1/7] 기업 리뷰 페이지 요청: {search_url}")
            
            # 페이지 로드
            try:
                # 기업 리뷰 페이지 로드
                print("[2/7] 기업 리뷰 페이지 로딩 중...")
                response = await page.goto(search_url, wait_until='domcontentloaded', timeout=10000)
                await asyncio.sleep(3)  # 페이지 로딩 대기
                if not response:
                    print("#ERROR# 기업 리뷰 페이지 로드 실패")
                    await browser.close()
                    return []
                print("[2/7] 기업 리뷰 페이지 로딩 완료")
                
                # 페이지 로딩 완료 대기
                print("[3/7] 페이지 안정화 대기 중...")
                if not await wait_for_page_load(page):
                    print("#ERROR# 기업 리뷰 페이지 로딩 시간 초과")
                    await browser.close()
                    return []
                print("[3/7] 페이지 안정화 완료")
                
                # ESC 키로 팝업 닫기 시도
                print("[4/7] 팝업 닫기 시도 중...")
                await close_popup_with_esc(page)
                print("[4/7] 팝업 닫기 완료")
                
                # 검색창 찾기 및 검색어 입력
                print("[5/7] 검색창 찾는 중...")
                search_input = await page.query_selector('xpath=/html/body/div/div/div/main/section/div/div[1]/div/div[1]/div/div/input')
                if not search_input:
                    print("#ERROR# 검색창을 찾을 수 없습니다.")
                    await browser.close()
                    return []
                print(f"[5/7] 검색창 발견, 검색어 입력: {query}")
                
                # 검색창 클릭하여 포커스
                await search_input.click()
                await asyncio.sleep(0.5)
                
                # 검색어 입력 (키보드 이벤트로 한 글자씩 입력)
                print("[5/7] 검색어 입력 중...")
                for char in query:
                    # 키보드 이벤트 발생
                    await page.evaluate(f'''
                        (char) => {{
                            const input = document.querySelector('input[type="text"]');
                            if (!input) {{
                                console.error('검색창을 찾을 수 없습니다.');
                                return;
                            }}
                            
                            // 키보드 이벤트 발생
                            const keydownEvent = new KeyboardEvent('keydown', {{
                                key: char,
                                code: 'Key' + char.toUpperCase(),
                                keyCode: char.charCodeAt(0),
                                which: char.charCodeAt(0),
                                bubbles: true,
                                cancelable: true
                            }});
                            
                            const keypressEvent = new KeyboardEvent('keypress', {{
                                key: char,
                                code: 'Key' + char.toUpperCase(),
                                keyCode: char.charCodeAt(0),
                                which: char.charCodeAt(0),
                                bubbles: true,
                                cancelable: true
                            }});
                            
                            const keyupEvent = new KeyboardEvent('keyup', {{
                                key: char,
                                code: 'Key' + char.toUpperCase(),
                                keyCode: char.charCodeAt(0),
                                which: char.charCodeAt(0),
                                bubbles: true,
                                cancelable: true
                            }});
                            
                            // 이벤트 발생
                            input.dispatchEvent(keydownEvent);
                            input.value += char;
                            input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                            input.dispatchEvent(keypressEvent);
                            input.dispatchEvent(keyupEvent);
                            input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                            
                            console.log('키보드 이벤트 발생:', char);
                        }}
                    ''', char)
                    await asyncio.sleep(0.5)  # 입력 간격
                    
                    # 자동완성 결과가 나타날 때까지 대기
                    try:
                        # 자동완성 드롭다운이 나타날 때까지 대기
                        await page.wait_for_selector('xpath=//div[contains(@class, "search_result") or contains(@class, "search-results")]', timeout=5000)
                        await asyncio.sleep(0.5)  # 결과 안정화 대기
                    except Exception as e:
                        print(f"#WARN# 자동완성 결과 대기 중 타임아웃: {str(e)}")
                        continue
                print("[5/7] 검색어 입력 완료")
                
                # 최종 자동완성 결과 대기
                print("[6/7] 최종 자동완성 결과 대기 중...")
                # /html/body/div[1]/div/div/main/section/div/div[1]/div/div[1]/div/div/div/div/ul/li 에 검색결과가 표시됨
                try:
                    # 자동완성 드롭다운이 나타날 때까지 대기
                    await page.wait_for_selector('xpath=/html/body/div[1]/div/div/main/section/div/div[1]/div/div[1]/div/div/div/div/ul/li', timeout=5000)
                    await asyncio.sleep(1)  # 결과 안정화 대기
                except Exception as e:
                    print("#ERROR# 자동완성 결과를 찾을 수 없습니다.")
                    await pause()  # 디버깅을 위한 일시 정지
                    await browser.close()
                    return []
                
                # 자동완성 결과에서 첫 번째 회사 선택
                print("[6/7] 검색 결과에서 회사 선택 중...")
                try:
                    # JavaScript로 검색 결과 선택 및 클릭
                    await page.evaluate(f'''
                        (searchQuery) => {{
                            // 검색 결과 컨테이너 찾기
                            const resultContainer = document.querySelector('ul');
                            if (!resultContainer) {{
                                console.error('검색 결과 컨테이너를 찾을 수 없습니다.');
                                return false;
                            }}
                            
                            // 모든 회사 항목 찾기
                            const companies = Array.from(resultContainer.querySelectorAll('li'));
                            console.log('검색된 회사 목록:', companies.map(c => c.textContent.trim()));
                            
                            // 검색어와 일치하는 회사 찾기
                            const targetCompany = companies.find(company => {{
                                const companyName = company.textContent.trim();
                                return companyName.includes(searchQuery);
                            }});
                            
                            if (!targetCompany) {{
                                console.error('검색어와 일치하는 회사를 찾을 수 없습니다:', searchQuery);
                                return false;
                            }}
                            
                            // 회사명 가져오기
                            const companyName = targetCompany.textContent.trim();
                            console.log('선택된 회사:', companyName);
                            
                            // 클릭 이벤트 발생
                            const clickEvent = new MouseEvent('click', {{
                                bubbles: true,
                                cancelable: true,
                                view: window
                            }});
                            targetCompany.dispatchEvent(clickEvent);
                            
                            return companyName;
                        }}
                    ''', query)
                    await asyncio.sleep(1)  # 클릭 후 대기
                except Exception as e:
                    print(f"#ERROR# 회사 항목 선택 중 오류: {str(e)}")
                    await browser.close()
                    return []
                
                # 회사명 가져오기
                company_name = await page.evaluate(f'''
                    (searchQuery) => {{
                        const companies = Array.from(document.querySelectorAll('ul li'));
                        const targetCompany = companies.find(company => {{
                            const companyName = company.textContent.trim();
                            return companyName.includes(searchQuery);
                        }});
                        return targetCompany ? targetCompany.textContent.trim() : null;
                    }}
                ''', query)
                
                if not company_name:
                    print("#ERROR# 회사명을 가져올 수 없습니다.")
                    await browser.close()
                    return []
                
                print(f"[6/7] 선택된 회사: {company_name}")
                
                # 회사명 정제 (Rating Score 부분 제거)
                company_name = re.sub(r'\s+Rating\s+Score.*$', '', company_name).strip()
                print(f"[6/7] 정제된 회사명: {company_name}")
                
                # 회사 페이지로 이동
                company_url = f"https://www.teamblind.com/kr/company/{company_name}"
                print(f"[6/7] 회사 페이지 요청: {company_url}")
                response = await page.goto(company_url, wait_until='domcontentloaded', timeout=10000)
                await asyncio.sleep(3)  # 페이지 로딩 대기
                
                if not response:
                    print("#ERROR# 회사 페이지 로드 실패")
                    await browser.close()
                    return []
                print("[6/7] 회사 페이지 로딩 완료")
                
                # 페이지 로딩 완료 대기
                print("[7/7] 회사 페이지 안정화 대기 중...")
                if not await wait_for_page_load(page):
                    print("#ERROR# 회사 페이지 로딩 시간 초과")
                    await browser.close()
                    return []
                print("[7/7] 회사 페이지 안정화 완료")
                
                # ESC 키로 팝업 닫기 시도
                print("[7/7] 팝업 닫기 시도 중...")
                await close_popup_with_esc(page)
                print("[7/7] 팝업 닫기 완료")
                
                # 회사 정보 추출
                companies = []
                
                try:
                    # 회사명 찾기
                    print("[7/7] 회사명 추출 중...")
                    # 회사명 : /html/body/div/div/div/main/section/div/div/div[1]/header/div/div[1]/div[2]/text()
                    # 스코어 : /html/body/div/div/div/main/section/div/div/div[1]/header/div/div[1]/div[3]/span/text()
                    # 회사소개 : /html/body/div/div/div/main/section/div/div/div[2]/div/div[2]/div/section[1] 
                    # 리뷰 : /html/body/div/div/div/main/section/div/div/div[2]/div/div[2]/div/div[1]/section
                    # 리뷰 (overall) : /html/body/div/div/div/main/section/div/div/div[2]/div/div[2]/div/div[1]/section/div[1]
                    # 리뷰 목록 : /html/body/div/div/div/main/section/div/div/div[2]/div/div[2]/div/div[1]/section/div[2]
                    
                    name_element = await page.query_selector('xpath=/html/body/div/div/div/main/section/div/div/div[1]/header/div/div[1]/div[2]')
                    if not name_element:
                        print("#WARN# 회사명 요소를 찾을 수 없음")
                        await pause()
                        await browser.close()
                        return []
                        
                    name = await name_element.inner_text()
                    name = name.strip()
                    if not name or len(name) < 2:
                        print(f"#ERROR# 유효하지 않은 회사명: {name}")
                        await browser.close()
                        return []
                    print(f"[7/7] 회사명 추출 완료: {name}")
                    
                    # 평점 찾기
                    print("[7/7] 평점 추출 중...")
                    rating = "정보 없음"
                    rating_element = await page.query_selector('xpath=/html/body/div/div/div/main/section/div/div/div[1]/header/div/div[1]/div[3]/span')
                    if rating_element:
                        rating_text = await rating_element.inner_text()
                        rating_text = rating_text.strip()
                        rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                        if rating_match:
                            rating = rating_match.group(1)
                    print(f"[7/7] 평점 추출 완료: {rating}")
                    
                    # 회사 소개 추출
                    print("[7/7] 회사 소개 추출 중...")
                    company_info = "정보 없음"
                    info_element = await page.query_selector('xpath=/html/body/div/div/div/main/section/div/div/div[2]/div/div[2]/div/section[1]')
                    if info_element:
                        company_info = await info_element.inner_text()
                        company_info = company_info.strip()
                    print(f"[7/7] 회사 소개 추출 완료: {company_info[:100]}...")
                    
                    # 리뷰 추출
                    print("[7/7] 리뷰 추출 중...")
                    reviews = []
                    
                    # 전체 리뷰 섹션
                    review_section = await page.query_selector('xpath=/html/body/div/div/div/main/section/div/div/div[2]/div/div[2]/div/div[1]/section')
                    if review_section:
                        # 전체 리뷰 요약
                        overall_element = await page.query_selector('xpath=/html/body/div/div/div/main/section/div/div/div[2]/div/div[2]/div/div[1]/section/div[1]')
                        if overall_element:
                            overall_text = await overall_element.inner_text()
                            reviews.append(f"전체 리뷰 요약:\n{overall_text.strip()}")
                        
                        # 개별 리뷰 목록
                        review_list = await page.query_selector('xpath=/html/body/div/div/div/main/section/div/div/div[2]/div/div[2]/div/div[1]/section/div[2]')
                        if review_list:
                            review_items = await review_list.query_selector_all('div')
                            for item in review_items:
                                review_text = await item.inner_text()
                                reviews.append(f"\n---\n{review_text.strip()}")
                    
                    print(f"[7/7] 리뷰 {len(reviews)}개 추출 완료")
                    
                    # 리뷰 요약 생성
                    print("[7/7] 리뷰 요약 생성 중...")
                    review_summary = await summarize_reviews(reviews, name)
                    print("[7/7] 리뷰 요약 생성 완료")
                    
                    # 회사명에서 (주) 제거 및 트리밍
                    clean_name = name.replace('(주)', '').strip()
                    print(f"[7/7] 정제된 회사명: {clean_name}")
                    
                    # 회사명에 특수문자가 포함된 경우 제외 (숫자는 허용)
                    if re.search(r'[+\-]', clean_name):
                        print(f"#WARN# 특수문자 포함된 회사명 제외: {clean_name}")
                        await browser.close()
                        return []
                    
                    companies.append({
                        'name': name,
                        'rating': rating,
                        'company_info': company_info,
                        'reviews': reviews,
                        'review_summary': review_summary
                    })
                    print("[7/7] 회사 정보 저장 완료")
                    
                except Exception as e:
                    print(f"#ERROR# 회사 정보 추출 중 오류: {str(e)}")
                    await browser.close()
                    return []
                
                # 브라우저 종료
                print("[7/7] 브라우저 종료 중...")
                await browser.close()
                print("[7/7] 브라우저 종료 완료")
                return companies
                
            except TimeoutError as e:
                print(f"#ERROR# 페이지 로딩 타임아웃: {str(e)}")
                await browser.close()
                return []
            
    except Exception as e:
        print(f"#ERROR# 오류가 발생했습니다: {str(e)}")
        return []

def wrap_text(text: str, width: int = 80) -> str:
    """텍스트를 지정된 너비에 맞게 줄바꿈 처리"""
    words = text.split()
    lines = []
    current_line = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) + 1 <= width:
            current_line.append(word)
            current_length += len(word) + 1
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
            current_length = len(word)
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return '\n'.join(lines)

def format_summary(text: str) -> str:
    """리뷰 요약을 인덱스별로 구분하여 포맷팅"""
    # 각 섹션을 구분
    sections = text.split('\n')
    formatted_sections = []
    current_index = None
    
    for section in sections:
        # 섹션이 비어있으면 건너뛰기
        if not section.strip():
            continue
            
        # 섹션 번호와 내용 분리
        if section.strip().startswith(('1.', '2.', '3.', '4.')):
            parts = section.split(':', 1)
            if len(parts) == 2:
                index = parts[0].strip()
                content = parts[1].strip()
                
                # 이전 인덱스와 현재 인덱스가 다를 경우 빈 줄 추가
                if current_index is not None and current_index != index:
                    formatted_sections.append('')
                
                # 내용을 80자 단위로 줄바꿈
                wrapped_content = wrap_text(content)
                # 들여쓰기 추가
                indented_content = '\n    '.join(wrapped_content.split('\n'))
                formatted_sections.append(f"{index}:\n    {indented_content}")
                current_index = index
            else:
                formatted_sections.append(section)
        else:
            formatted_sections.append(section)
    
    return '\n'.join(formatted_sections)

def main():
    """메인 함수"""
    if len(sys.argv) != 2:
        print("사용법: python jpl.py <검색어>")
        sys.exit(1)
    
    query = sys.argv[1]
    # print(f"검색어: {query}")
    
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
        print(f"\n회사 소개:")
        print("-" * 50)
        print(company['company_info'])
        print("-" * 50)
        
        print("\n리뷰 요약:")
        print("=" * 50)
        if company['review_summary']:
            print(format_summary(company['review_summary']))
        else:
            print("리뷰 요약을 생성할 수 없습니다.")
        print("=" * 50)
        print("\n")
    
    # JSON 파일로 저장
    if len(companies) > 0:
        output_file = f"/tmp/jobplanet_{query}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(companies, f, ensure_ascii=False, indent=2)
        print(f"\n결과가 {output_file}에 저장되었습니다.")
        
        # PostgreSQL에 저장
        try:
            # 현재 스크립트의 디렉토리 경로 가져오기
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # save_to_db.py의 절대 경로 생성
            save_to_db_path = os.path.join(current_dir, 'save_to_db.py')
            subprocess.run(['python', save_to_db_path, output_file], check=True)
        except subprocess.CalledProcessError as e:
            print(f"#ERROR# 데이터베이스 저장 중 오류: {str(e)}")
        except Exception as e:
            print(f"#ERROR# 데이터베이스 저장 중 오류: {str(e)}")

if __name__ == "__main__":
    main()