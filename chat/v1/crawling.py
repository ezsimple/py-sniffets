from sqlalchemy import create_engine, Column, Text, Integer, DateTime, func, Index, Sequence, UniqueConstraint
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


# SQLAlchemy ORM 설정
Base = declarative_base()

class MinoQuote(Base):
    __tablename__ = 'MinoQuotes'
    
    id = Column(Integer, Sequence('minoquote_id_seq'), primary_key=True, nullable=False)  # 자동 번호 생성 및 유일성 보장
    q = Column(Text, nullable=False)  # 명언, 복합 키의 일부
    a = Column(Text, nullable=False)  # 저자, 복합 키의 일부
    h = Column(Text)  # 주제
    reg_date = Column(DateTime, server_default=func.now())  # 저장일시

    '''
    복합 기본 키 및 유일 제약 조건 설정
    UniqueConstraint를 import하여 복합 유일 제약 조건을 설정할 수 있도록 하였습니다.
    이제 이 코드로 MinoQuote 클래스를 정의하면 q와 a의 조합이 유일하게 유지됩니다. 
    '''
    __table_args__ = (
        Index('idx_minoquote_id', 'id'),  # 인덱스 생성
        UniqueConstraint('q', 'a', name='uq_minoquote_q_a')  # q, a에 유일 제약 조건 추가
    )

# 데이터베이스 연결
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def add_quote(data):
    session = Session()
    new_quote = MinoQuote(q=data['q'], a=data['a'], h=data['h'])
    
    try:
        session.add(new_quote)
        session.commit()
        logger.debug("Quote added successfully.")
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
