#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# -------------------------------------------------
# 사용법 
# -------------------------------------------------
# from TelegramSimpleBot import TelegramSimpleBot
# bot = TelegramSimpleBot()
# bot.send_message("이것은 테스트 메시지입니다.")

import os
import requests
import logging
from typing import Optional
from dotenv import load_dotenv
from datetime import datetime

# .env 파일 로드
load_dotenv()

class TelegramSimpleBot:
    """텔레그램 봇을 위한 간단한 클래스"""
    
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN 환경변수가 설정되지 않았습니다.")
        if not self.chat_id:
            raise ValueError("TELEGRAM_CHAT_ID 환경변수가 설정되지 않았습니다.")
        
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.logger = logging.getLogger(__name__)
    
    def send_message(self, message: str) -> bool:
        """
        텔레그램으로 메시지를 발송합니다.
        
        Args:
            message (str): 발송할 메시지
            
        Returns:
            bool: 발송 성공 여부
        """
        try:
            url = f"{self.api_url}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML'  # HTML 형식 지원
            }
            
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if result.get('ok'):
                self.logger.info("텔레그램 메시지 발송 성공")
                return True
            else:
                self.logger.error(f"텔레그램 메시지 발송 실패: {result}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"텔레그램 API 요청 중 오류: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"텔레그램 메시지 발송 중 오류: {str(e)}")
            return False
    
    def send_photo(self, photo_path: str, caption: Optional[str] = None) -> bool:
        """
        텔레그램으로 사진을 발송합니다.
        
        Args:
            photo_path (str): 사진 파일 경로
            caption (str, optional): 사진 설명
            
        Returns:
            bool: 발송 성공 여부
        """
        try:
            if not os.path.exists(photo_path):
                self.logger.error(f"사진 파일을 찾을 수 없습니다: {photo_path}")
                return False
            
            url = f"{self.api_url}/sendPhoto"
            data = {
                'chat_id': self.chat_id
            }
            
            if caption:
                data['caption'] = caption
            
            with open(photo_path, 'rb') as photo:
                files = {'photo': photo}
                response = requests.post(url, data=data, files=files, timeout=30)
                response.raise_for_status()
            
            result = response.json()
            if result.get('ok'):
                self.logger.info("텔레그램 사진 발송 성공")
                return True
            else:
                self.logger.error(f"텔레그램 사진 발송 실패: {result}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"텔레그램 API 요청 중 오류: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"텔레그램 사진 발송 중 오류: {str(e)}")
            return False
    
    def get_me(self) -> Optional[dict]:
        """
        봇 정보를 가져옵니다.
        
        Returns:
            dict: 봇 정보 또는 None
        """
        try:
            url = f"{self.api_url}/getMe"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if result.get('ok'):
                return result.get('result')
            else:
                self.logger.error(f"봇 정보 가져오기 실패: {result}")
                return None
                
        except Exception as e:
            self.logger.error(f"봇 정보 가져오기 중 오류: {str(e)}")
            return None

def test_bot():
    """봇 테스트 함수"""
    try:
        bot = TelegramSimpleBot()
        
        # 봇 정보 확인
        bot_info = bot.get_me()
        if bot_info:
            print(f"봇 이름: {bot_info.get('first_name')}")
            print(f"봇 사용자명: @{bot_info.get('username')}")
        
        # 테스트 메시지 발송
        test_message = "🤖 텔레그램 봇 테스트 메시지입니다!\n\n"
        test_message += "✅ 봇이 정상적으로 작동하고 있습니다.\n"
        test_message += "⏰ 테스트 시간: " + str(datetime.now())
        
        success = bot.send_message(test_message)
        if success:
            print("✅ 테스트 메시지 발송 성공!")
        else:
            print("❌ 테스트 메시지 발송 실패!")
            
    except Exception as e:
        print(f"❌ 봇 테스트 중 오류: {str(e)}")

if __name__ == "__main__":
    test_bot()

