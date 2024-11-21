# %%
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

def vacuum():
    load_dotenv()
    DATABASE_URL = os.getenv("DATABASE_URL", None)
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL is not set in the environment variables.")

    # 별도의 연결로 분리
    engine = create_engine(DATABASE_URL, echo=True)
    # VACUUM을 독립적으로 실행 (트랜잭션에서 분리해야만 함)
    with engine.connect() as connection:
        # autocommit 모드 활성화 - 트랜잭션 제거
        connection.execution_options(isolation_level="AUTOCOMMIT")
        connection.execute(text('VACUUM FULL;'))  # VACUUM 명령어 실행

if __name__ == "__main__":
    vacuum()
