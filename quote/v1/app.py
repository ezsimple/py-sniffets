from fastapi import FastAPI, HTTPException, APIRouter
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.future import select
import random
from dotenv import load_dotenv
from logging.handlers import TimedRotatingFileHandler
import logging
from datetime import datetime
import os, sys

# 현재 스크립트의 경로를 기준으로 PYTHONPATH 추가
current_dir = os.path.dirname(os.path.abspath(__file__))  # 현재 파일의 절대 경로
parent_dir = os.path.abspath(os.path.join(current_dir, '../../'))  # 부모 디렉토리 경로
sys.path.append(parent_dir)  # PYTHONPATH에 추가
from chat.v1.models.models import MinoQuote

# 환경 변수 로드
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
    raise ValueError("DATABASE_URL is not set in the environment variables.")

PREFIX = os.getenv("PREFIX", "/quotes")
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", 3355))

# 데이터베이스 비동기 엔진 생성
engine = create_async_engine(DATABASE_URL, echo=True)

# 비동기 세션 생성
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# 로깅 설정
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

# FastAPI 인스턴스 생성
app = FastAPI()
router = APIRouter(prefix=PREFIX)

@router.get("/")
async def get_random_quote():
    async with async_session() as session:
        # 총 인용구 개수 조회
        total_quotes_query = select(func.count(MinoQuote.id))
        total_quotes = await session.execute(total_quotes_query)
        total_count = total_quotes.scalar() or 0

        if total_count == 0:
            raise HTTPException(status_code=404, detail="No quotes available.")

        # 랜덤 인덱스 생성
        random_index = random.randint(0, total_count - 1)

        # 랜덤 인용구 조회
        random_quote_query = select(MinoQuote).offset(random_index).limit(1)
        logger.debug(str(random_quote_query))
        result = await session.execute(random_quote_query)
        quote = result.scalar_one_or_none()

        if quote is None:
            raise HTTPException(status_code=404, detail="Quote not found.")

        # 응답 포맷팅
        res = [{"q": quote.q, "a": quote.a, "h": quote.h}]
        return res


app.include_router(router)

# FastAPI 서버 실행
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
