from sqlalchemy import text
from sqlalchemy import exc
import httpx
import asyncio
from models.models import MinoQuote
from logger import LoggerSetup
from database import engine, SessionLocal, Base

'''
명언 카드는 포트폴리오 개념의 서비스이므로,
일단 연동 서버측 명언 데이터를 보관하도록 한다.
'''
Base.metadata.create_all(engine)

# 로깅 설정
logger_setup = LoggerSetup()
logger = logger_setup.get_logger()

def add_quote(data):
    # with 문을 사용하여 세션 관리
    with SessionLocal() as session:
        new_quote = MinoQuote(q=data['q'], a=data['a'], t=data['h'])
        try:
            session.add(new_quote)
            session.commit()
            logger.debug("Quote added successfully.")
            return new_quote
        except exc.IntegrityError:
            session.rollback()  # 오류 발생 시 롤백
            logger.warning(f"Quote already exists, skipping... {data['q']}")
            # 이미 존재하는 경우 None 반환
            existing_quote = session.query(MinoQuote).filter_by(q=data['q'], a=data['a']).first()
            return existing_quote

async def scrape_quote():
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
    asyncio.run(scrape_quote())

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