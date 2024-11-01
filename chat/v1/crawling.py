from sqlalchemy import create_engine, Column, Text, Integer, DateTime, func, Index, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import exc
import httpx
from dotenv import load_dotenv
import os
import asyncio
from models.models import MinoQuote, Base

'''
명언 카드는 포트폴리오 개념의 서비스이므로,
일단 연동 서버측 명언 데이터를 보관하도록 한다.
'''

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
    raise ValueError("DATABASE_URL is not set in the environment variables.")

# SQLAlchemy ORM 설정
Base = declarative_base()

class MinoQuote(Base):
    __tablename__ = 'MinoQuotes'
    
    id = Column(Integer, Sequence('minoquote_id_seq'), nullable=False)  # 자동 번호 생성
    # 복합 기본 키 설정
    q = Column(Text, primary_key=True, nullable=False)  # 명언
    a = Column(Text, primary_key=True, nullable=False)  # 저자
    h = Column(Text)  # 주제
    reg_date = Column(DateTime, server_default=func.now())  # 저장일시

    # 인덱스 생성
    __table_args__ = (
        Index('idx_minoquote_id', 'id'),  # 인덱스 생성
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
        print("Quote added successfully.")
    except exc.IntegrityError:
        session.rollback()
        print("Quote already exists, skipping...")
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
            add_quote(data[0])
            return data
        return {"content": "격언을 가져오는 데 실패했습니다.", "author": "알 수 없음"}

if __name__ == "__main__":
    asyncio.run(ask_quote())
