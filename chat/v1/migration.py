from sqlalchemy import create_engine, Column, Integer, Text, DateTime, Sequence, func, Index, UniqueConstraint, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import insert
from dotenv import load_dotenv
from models.models import MinoQuote, Base
import os

# 환경 변수 로드
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
    raise ValueError("DATABASE_URL is not set in the environment variables.")

# 데이터베이스 엔진 생성
engine = create_engine(DATABASE_URL)

# 테이블 생성
Base.metadata.create_all(engine)

try:
    # minoquotes_copy 테이블에서 데이터 읽기
    with engine.connect() as connection:
        results = connection.execute(text("SELECT q, a, h FROM minoquotes_copy"))

        # 데이터가 있는지 확인
        if results.rowcount == 0:
            print("minoquotes_copy 테이블에 데이터가 없습니다.")
        else:
            for row in results:
                q_value = row[0]
                a_value = row[1]
                h_value = row[2]
                
                print(f"Inserting: q='{q_value}', a='{a_value}', h='{h_value}'")  # 로그 추가
                
                # 중복 row skip 기능
                insert_stmt = insert(MinoQuote).values(q=q_value, a=a_value, h=h_value)
                insert_stmt = insert_stmt.on_conflict_do_nothing(index_elements=['q', 'a']) # 충돌시 Sequence 증가되 버림
                connection.execute(insert_stmt)

            # 시퀀스를 현재 최대 id 값으로 재설정
            max_id_query = text('SELECT MAX(id) FROM "MinoQuotes"') 
            max_id = connection.execute(max_id_query).scalar() or 0
            reset_sequence_query = text(f"SELECT setval('minoquote_id_seq', {max_id})")
            connection.execute(reset_sequence_query)

            # 커넥션을 통해 커밋
            connection.commit()

    print("데이터 삽입 완료")

except Exception as e:
    print(f"오류 발생: {e}")

'''
-- 참고 쿼리
SELECT id, COUNT(*) as cnt
FROM "MinoQuotes" a
GROUP BY id 
having count(id) > 1
ORDER BY id ;

SELECT *
FROM information_schema.table_constraints
WHERE constraint_name = 'idx_minoquote_id';

CREATE TABLE MinoQuotes_copy AS
SELECT *
from public."MinoQuotes" mq ;

WITH RECURSIVE id_series AS (
    SELECT generate_series(1, (select MAX(id) FROM "MinoQuotes")) AS id
)
SELECT id_series.id
FROM id_series
LEFT JOIN "MinoQuotes" ON id_series.id = "MinoQuotes".id
WHERE "MinoQuotes".id IS NULL;

DROP SEQUENCE IF EXISTS minoquote_id_seq;
'''