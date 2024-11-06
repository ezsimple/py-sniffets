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
from models.models import MinoQuote2, Base
import re
import csv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
    raise ValueError("DATABASE_URL is not set in the environment variables.")

current_dir = os.path.dirname(os.path.abspath(__file__))
log_dir = os.path.join(current_dir, "log")
os.makedirs(log_dir, exist_ok=True)

current_date = datetime.now().strftime("%Y-%m-%d")
log_file_name = f"{os.path.basename(__file__)}-{current_date}.log"
log_file_path = os.path.join(log_dir, log_file_name)
handler = TimedRotatingFileHandler(log_file_path, when="midnight", interval=1, backupCount=7)
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(filename)s - line:%(lineno)d - %(message)s'))

logging.basicConfig(
    level=logging.WARNING,
    handlers=[
        handler,
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# 데이터베이스 연결
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

async def add_quote(data):
    session = Session()
    new_quote = MinoQuote2(q=data['q'], a=data['a'], t=data['t'])
    
    try:
        session.add(new_quote)
        session.commit()
        logger.debug("Quote added successfully.")

        # 시퀀스를 현재 최대 id 값으로 재설정
        max_id2_query = text('SELECT MAX(id) FROM "MinoQuotes2"') 
        max_id2 = session.execute(max_id2_query).scalar() or 0
        reset_sequence_query = text(f"SELECT setval('minoquote2_id_seq', {max_id2})")
        session.execute(reset_sequence_query)
    except exc.IntegrityError:
        session.rollback()
        logger.warning(f"Quote already exists, skipping... {data['q']}")
    except exc.DataError as e: # 데이터 길이 제한과 같은 데이터 유효성 오류를 처리하기 위해
        session.rollback()
        logger.warning(f"Data error: {str(e)} for quote: {data['q']}")  # 구체적인 오류 메시지 로깅
    except exc.SQLAlchemyError as e:
        session.rollback()
        logger.warning(f"SQLAlchemy error occurred: {str(e)} for quote: {data['q']}")
    finally:
        session.close()

async def add_quotes(quotes):
    session = Session()
    try:
        # 새로운 인용구 객체 생성
        new_quotes = [MinoQuote2(q=quote['q'], a=quote['a'], t=quote['t']) for quote in quotes]
        session.bulk_save_objects(new_quotes)  # 배치 삽입
        session.commit()
        logger.debug(f"{len(new_quotes)} quotes added successfully.")

        # 시퀀스를 현재 최대 id 값으로 재설정
        max_id_query = text('SELECT MAX(id) FROM "MinoQuotes2"')  # 테이블 이름 수정
        max_id = session.execute(max_id_query).scalar() or 0
        reset_sequence_query = text(f"SELECT setval('minoquote2_id_seq', {max_id})")
        session.execute(reset_sequence_query)
    except exc.IntegrityError:
        session.rollback()
        logger.warning("Some quotes already exist, skipping duplicates.")
    except exc.DataError as e:  # 데이터 오류 처리
        session.rollback()
        logger.warning(f"Data error: {str(e)}")
    except exc.SQLAlchemyError as e:
        session.rollback()
        logger.warning(f"SQLAlchemy error occurred: {str(e)}")
    finally:
        session.close()

async def read_quotes():
    file_list = [f for f in os.listdir() if f.startswith("quotes-") and f.endswith(".csv")]
    count = 0
    err_leng_count = 0
    err_not_eng_count = 0
    err_malformed_count = 0
    for f in file_list:
        with open(f, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                if len(row) == 3:
                    quote, author, tag = row

                    allowed_special_chars = r'\'`.,:!@#%$&*[]()-\-+=~?\\n\\t'
                    cleaned_text = re.sub(fr'[^a-zA-Z0-9\s{allowed_special_chars}]', ' ', quote)
                    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
                    
                    words = re.findall(r'\b\w+\b', cleaned_text)
                    if not all(re.fullmatch(r'[a-zA-Z]+', word) for word in words):
                        err_not_eng_count += 1 
                        logger.error(quote)
                        continue

                    if len(quote) > 1024:
                        err_leng_count += 1
                        leng_quote = len(quote)
                        logger.error(f"Quote is too long - length:{leng_quote}, {quote}")
                        continue

                    count += 1
                    yield {
                        "q": quote.strip(),
                        "a": author.strip(),
                        "t": tag.strip()
                    }
                else:
                    err_malformed_count += 1
                    logger.warning(f"Skipping malformed line in file {f}: {row}")

    logger.debug(f'total add count : {count}, error_not_eng:{err_not_eng_count}, error_leng:{err_leng_count}, error_malformed:{err_malformed_count}')

BATCH_SIZE = 10
async def main():
    quotes = []
    async for quote in read_quotes():
        quotes.append(quote)

        # 배치 크기만큼 모였을 때 추가
        if len(quotes) >= BATCH_SIZE:
            await add_quotes(quotes)
            quotes.clear()  # 리스트 초기화

    # 남은 인용구 추가
    if quotes:  
        await add_quotes(quotes)

if __name__ == "__main__":
    asyncio.run(main())
