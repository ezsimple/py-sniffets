#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 목적 : 평생교육이용권 신청.접수 공지 확인용
# 기능 
# crontab 으로 하루 한번 실행 예정.
# 주의 지역별 URL이 다름
# 경기_URL : 
# 충청_URL : https://www.lllcard.kr/reg/chungnam/cop/bbs/selectBoardList.do
# 충청_현재_목록수 : 9건
# 충청_URL 을 접속 -> 평생교육 검색어 입력 & 조회 -> 검색 결과 목록수 확인 -> 충청_현재_목록수와 다를 경우 
# from TelegramSimpleBot import TelegramSimpleBot
# bot = TelegramSimpleBot()
# bot.send_message("평생교육 새로운 공지가 나왔습니다.") 보내기

import os
import sys
import re
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional
from playwright.async_api import async_playwright, TimeoutError
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('lifelong_edu.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LifelongEducationMonitor:
    """평생교육이용권 공지 모니터링 클래스"""
    
    def __init__(self):
        self.regions = {
            'chungnam': {
                'name': '충청남도',
                'url': 'https://www.lllcard.kr/reg/chungnam/cop/bbs/selectBoardList.do',
                'current_count': 9,
                'search_keyword': '평생교육'
            },
            'gyeonggi': {
                'name': '경기도',
                'url': '',  # URL이 비어있음 - 추후 추가 필요
                'current_count': 0,
                'search_keyword': '평생교육'
            }
        }
        self.config_file = 'lifelong_edu_config.json'
        self.load_config()
    
    def load_config(self):
        """설정 파일에서 현재 목록수 로드"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    for region, data in config.items():
                        if region in self.regions:
                            self.regions[region]['current_count'] = data.get('current_count', 0)
                logger.info("설정 파일에서 현재 목록수 로드 완료")
            else:
                logger.info("설정 파일이 없어 기본값 사용")
        except Exception as e:
            logger.error(f"설정 파일 로드 중 오류: {str(e)}")
    
    def save_config(self):
        """현재 목록수를 설정 파일에 저장"""
        try:
            config = {}
            for region, data in self.regions.items():
                config[region] = {
                    'current_count': data['current_count'],
                    'last_updated': datetime.now().isoformat()
                }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            logger.info("설정 파일 저장 완료")
        except Exception as e:
            logger.error(f"설정 파일 저장 중 오류: {str(e)}")
    
    async def check_region_notices(self, region_key: str) -> Optional[int]:
        """특정 지역의 공지 목록수 확인"""
        region = self.regions.get(region_key)
        if not region:
            logger.error(f"알 수 없는 지역: {region_key}")
            return None
        
        if not region['url']:
            logger.warning(f"{region['name']} URL이 설정되지 않았습니다.")
            return None
        
        try:
            async with async_playwright() as p:
                # 브라우저 설정
                browser = await p.chromium.launch(
                    headless=True,
                    args=['--disable-dev-shm-usage', '--no-sandbox']
                )
                
                # 컨텍스트 생성
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
                )
                
                # 페이지 생성
                page = await context.new_page()
                page.set_default_timeout(30000)  # 30초 타임아웃
                
                logger.info(f"{region['name']} 공지사항 페이지 접속 중...")
                
                # 페이지 로드
                response = await page.goto(region['url'], wait_until='domcontentloaded')
                if not response:
                    logger.error(f"{region['name']} 페이지 로드 실패")
                    await browser.close()
                    return None
                
                await asyncio.sleep(3)  # 페이지 로딩 대기
                
                # 검색창 찾기
                logger.info(f"{region['name']} 검색창 찾는 중...")
                search_input = await page.query_selector('input[name="searchKeyword"], input[type="text"], #searchKeyword')
                
                if not search_input:
                    logger.error(f"{region['name']} 검색창을 찾을 수 없습니다.")
                    await browser.close()
                    return None
                
                # 검색어 입력
                logger.info(f"{region['name']} 검색어 입력: {region['search_keyword']}")
                await search_input.click()
                await search_input.fill(region['search_keyword'])
                await asyncio.sleep(1)
                
                # 검색 버튼 클릭
                search_button = await page.query_selector('button[type="submit"], input[type="submit"], .btn_search, #searchBtn')
                if search_button:
                    await search_button.click()
                    logger.info(f"{region['name']} 검색 실행")
                else:
                    # Enter 키로 검색
                    await search_input.press('Enter')
                    logger.info(f"{region['name']} Enter 키로 검색 실행")
                
                await asyncio.sleep(3)  # 검색 결과 로딩 대기
                
                # 검색 결과 목록수 확인
                logger.info(f"{region['name']} 검색 결과 확인 중...")
                
                # 여러 가지 가능한 선택자로 목록수 확인
                count_selectors = [
                    '.total_count',
                    '.count',
                    '.result_count',
                    'span:contains("건")',
                    'div:contains("건")',
                    '.board_list .total',
                    '#totalCount'
                ]
                
                result_count = None
                for selector in count_selectors:
                    try:
                        count_element = await page.query_selector(selector)
                        if count_element:
                            count_text = await count_element.inner_text()
                            # 숫자 추출
                            numbers = re.findall(r'\d+', count_text)
                            if numbers:
                                result_count = int(numbers[0])
                                logger.info(f"{region['name']} 검색 결과: {result_count}건")
                                break
                    except Exception as e:
                        logger.debug(f"선택자 {selector} 실패: {str(e)}")
                        continue
                
                # 목록수 확인이 실패한 경우, 실제 목록 항목 수를 세기
                if result_count is None:
                    logger.info(f"{region['name']} 목록수 직접 계산 중...")
                    list_items = await page.query_selector_all('tr, .list_item, .board_item, .item')
                    result_count = len(list_items)
                    logger.info(f"{region['name']} 실제 목록 항목 수: {result_count}건")
                
                await browser.close()
                return result_count
                
        except TimeoutError as e:
            logger.error(f"{region['name']} 페이지 로딩 타임아웃: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"{region['name']} 공지 확인 중 오류: {str(e)}")
            return None
    
    async def send_telegram_notification(self, region_name: str, old_count: int, new_count: int):
        """텔레그램 알림 발송"""
        try:
            from TelegramSimpleBot import TelegramSimpleBot
            
            bot = TelegramSimpleBot()
            message = f"🔔 평생교육이용권 새로운 공지가 나왔습니다!\n\n"
            message += f"📍 지역: {region_name}\n"
            message += f"📊 이전 목록수: {old_count}건\n"
            message += f"📊 현재 목록수: {new_count}건\n"
            message += f"📈 증가: {new_count - old_count}건\n"
            message += f"⏰ 확인시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            bot.send_message(message)
            logger.info(f"텔레그램 알림 발송 완료: {region_name}")
            
        except ImportError:
            logger.warning("TelegramSimpleBot 모듈을 찾을 수 없습니다. 알림을 발송하지 않습니다.")
        except Exception as e:
            logger.error(f"텔레그램 알림 발송 중 오류: {str(e)}")
    
    async def monitor_all_regions(self):
        """모든 지역의 공지사항 모니터링"""
        logger.info("평생교육이용권 공지 모니터링 시작")
        
        for region_key, region_data in self.regions.items():
            if not region_data['url']:
                logger.warning(f"{region_data['name']} URL이 설정되지 않아 건너뜁니다.")
                continue
            
            logger.info(f"{region_data['name']} 모니터링 시작")
            
            # 현재 목록수 확인
            current_count = await self.check_region_notices(region_key)
            
            if current_count is not None:
                old_count = region_data['current_count']
                
                logger.info(f"{region_data['name']} - 이전: {old_count}건, 현재: {current_count}건")
                
                # 목록수가 변경된 경우
                if current_count != old_count:
                    logger.info(f"{region_data['name']} 새로운 공지 발견!")
                    
                    # 텔레그램 알림 발송
                    await self.send_telegram_notification(
                        region_data['name'], 
                        old_count, 
                        current_count
                    )
                    
                    # 설정 업데이트
                    self.regions[region_key]['current_count'] = current_count
                    self.save_config()
                    
                    logger.info(f"{region_data['name']} 설정 업데이트 완료")
                else:
                    logger.info(f"{region_data['name']} 새로운 공지 없음")
            else:
                logger.error(f"{region_data['name']} 목록수 확인 실패")
        
        logger.info("평생교육이용권 공지 모니터링 완료")

async def main():
    """메인 함수"""
    try:
        monitor = LifelongEducationMonitor()
        await monitor.monitor_all_regions()
    except Exception as e:
        logger.error(f"모니터링 중 오류 발생: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
