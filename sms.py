#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 사용법 : python sms.py 01039960883 변작된 발신번호 발송 실패 테스트

import sys
import os
from dotenv import load_dotenv
from solapi import SolapiMessageService
from solapi.model import RequestMessage

# .env 파일에서 환경변수 로드
load_dotenv()

def send_sms(to_number: str, message_text: str) -> bool:
    """
    SMS를 발송하는 함수
    
    Args:
        to_number (str): 수신번호
        message_text (str): 발송할 메시지
        
    Returns:
        bool: 발송 성공 여부
    """
    try:
        # 환경변수에서 API 키와 발신번호 가져오기
        api_key = os.getenv("SOL_API_KEY")
        api_secret = os.getenv("SOL_API_SECRET")
        from_number = os.getenv("SOL_API_HP")
        print(from_number)
        
        # 필수 환경변수 확인
        if not api_key:
            print("ERROR: SOL_API_KEY 환경변수가 설정되지 않았습니다.")
            return False
        if not api_secret:
            print("ERROR: SOL_API_SECRET 환경변수가 설정되지 않았습니다.")
            return False
        if not from_number:
            print("ERROR: SOL_HP 환경변수가 설정되지 않았습니다.")
            return False
        
        # 수신번호 형식 검증 (010으로 시작하는 11자리 숫자)
        if not to_number.startswith('010') or len(to_number) != 11 or not to_number.isdigit():
            print(f"ERROR: 유효하지 않은 수신번호 형식입니다: {to_number}")
            print("수신번호는 010으로 시작하는 11자리 숫자여야 합니다.")
            return False
        
        # 발신번호 형식 검증
        if not from_number.startswith('010') or len(from_number) != 11 or not from_number.isdigit():
            print(f"ERROR: 유효하지 않은 발신번호 형식입니다: {from_number}")
            print("발신번호는 010으로 시작하는 11자리 숫자여야 합니다.")
            return False
        
        # SolapiMessageService 초기화
        message_service = SolapiMessageService(
            api_key=api_key,
            api_secret=api_secret
        )
        
        # 메시지 모델 생성
        message = RequestMessage(
            from_=from_number,
            to=to_number,
            text=message_text
        )
        
        # 메시지 발송
        print(f"SMS 발송 중...")
        print(f"발신번호: {from_number}")
        print(f"수신번호: {to_number}")
        print(f"메시지: {message_text}")
        
        response = message_service.send(message)
        
        # 발송 결과 출력
        print("\n✅ 메시지 발송 성공!")
        print(f"Group ID: {response.group_info.group_id}")
        print(f"요청한 메시지 개수: {response.group_info.count.total}")
        print(f"성공한 메시지 개수: {response.group_info.count.registered_success}")
        print(f"실패한 메시지 개수: {response.group_info.count.registered_failed}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 메시지 발송 실패: {str(e)}")
        return False

def main():
    """메인 함수"""
    # 명령행 인수 확인
    if len(sys.argv) < 3:
        print("사용법: python sms.py <수신번호> <메시지>")
        print("예시: python sms.py 01012345678 '안녕하세요! SMS 테스트입니다.'")
        print("\n주의사항:")
        print("- 수신번호는 010으로 시작하는 11자리 숫자여야 합니다.")
        print("- .env 파일에 다음 환경변수가 설정되어야 합니다:")
        print("  SOL_API_KEY=your_api_key")
        print("  SOL_API_SECRET=your_api_secret")
        print("  SOL_HP=01012345678 (발신번호)")
        sys.exit(1)
    
    # 명령행 인수 파싱
    to_number = sys.argv[1]
    message_text = ' '.join(sys.argv[2:])
    
    print("=" * 50)
    print("SMS 발송 프로그램")
    print("=" * 50)
    
    # SMS 발송
    success = send_sms(to_number, message_text)
    
    if success:
        print("\n🎉 SMS 발송이 완료되었습니다!")
    else:
        print("\n💥 SMS 발송에 실패했습니다.")
        sys.exit(1)

if __name__ == "__main__":
    main()