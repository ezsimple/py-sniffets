import os
import sys
sys.path.append('/home/ubuntu/.pyenv/versions/3.10.14/envs/머신러닝/lib/python3.10/site-packages')

# Flask 애플리케이션을 생성하는 함수 임포트
from app import create_app

# 환경 변수 설정
env = os.getenv('APPLICATION_MODE', 'PRODUCTION')

# Flask 애플리케이션 인스턴스 생성
application = create_app()

if __name__ == "__main__":
    # 개발 환경에서 실행할 때는 기본 웹서버로 실행
    application.run()
