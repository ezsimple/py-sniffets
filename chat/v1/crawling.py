from sqlalchemy import create_engine, Column, Text, Integer, DateTime, func, Index, Sequence, UniqueConstraint, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import exc
import httpx
from dotenv import load_dotenv
import os
import asyncio
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
from models.models import MinoQuote, Base

'''
명언 카드는 포트폴리오 개념의 서비스이므로,
일단 연동 서버측 명언 데이터를 보관하도록 한다.
'''

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
    raise ValueError("DATABASE_URL is not set in the environment variables.")

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

# 데이터베이스 연결
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def add_quote(data):
    session = Session()
    new_quote = MinoQuote(q=data['q'], a=data['a'], t=data['h'])
    
    try:
        session.add(new_quote)
        session.commit()
        logger.debug("Quote added successfully.")

        # 시퀀스를 현재 최대 id 값으로 재설정
        max_id_query = text('SELECT MAX(id) FROM "MinoQuotes"') 
        max_id = session.execute(max_id_query).scalar() or 0
        reset_sequence_query = text(f"SELECT setval('minoquote_id_seq', {max_id})")
        session.execute(reset_sequence_query)
    except exc.IntegrityError:
        session.rollback()
        logger.warning(f"Quote already exists, skipping... {data['q']}")
    finally:
        session.close()

async def ask_quote():
    '''
    예시 포맷:
    quote_data = {
        "q": "Quality means doing it right when no one is looking.",
        "a": "Henry Ford",
        "h": "<blockquote>“Quality means doing it right when no one is looking.” — <footer>Henry Ford</footer></blockquote>"
    }
    '''
    async with httpx.AsyncClient() as client:
        response = await client.get("https://zenquotes.io/api/random")
        if response.status_code == 200:
            data = response.json()
            if 'zenquotes.io' in data[0]['a']:
                logger.warning(f'Warning: {data[0]}')
                return data

            add_quote(data[0])
            return data
        return {"content": "격언을 가져오는 데 실패했습니다.", "author": "알 수 없음"}

if __name__ == "__main__":
    asyncio.run(ask_quote())

'''
일일 명언  수집 통계
- total_count : 전체 명언수
- today_add_count : 금일 추가된 명언수
- today_add_ratio : 금일 추가된 요청 대비  명언 효율
WITH yesterday AS (
    SELECT 
        max(id) AS max_id,
        min(id) as min_id
    FROM 
        "MinoQuotes"
    WHERE 
        reg_date::date = CURRENT_DATE - INTERVAL '1 day'  -- 어제의 날짜
),
today AS (
    SELECT 
        count(*) AS total_count
    FROM 
        "MinoQuotes"
    WHERE 
        reg_date::date = CURRENT_DATE  -- 오늘의 날짜
)
SELECT 
    coalesce((SELECT count(*) FROM "MinoQuotes" mq1 ))AS total_count,
    COALESCE((SELECT total_count FROM today), 0) AS today_add_count,
    COALESCE((SELECT total_count FROM today), 0) * 100.0 / NULLIF((SELECT (max_id - min_id) FROM yesterday), 0) AS today_add_ratio
'''