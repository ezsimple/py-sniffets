from sqlalchemy import create_engine, Column, Integer, Text, DateTime, Sequence, func, Index, UniqueConstraint, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import insert
from dotenv import load_dotenv
import os

# 환경 변수 로드
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
    raise ValueError("DATABASE_URL is not set in the environment variables.")

Base = declarative_base()

# MinoQuote 클래스 정의
class MinoQuote(Base):
    __tablename__ = 'MinoQuotes'
    
    id = Column(Integer, Sequence('minoquote_id_seq'), primary_key=True, nullable=False)
    q = Column(Text, nullable=False)
    a = Column(Text, nullable=False)
    h = Column(Text)
    reg_date = Column(DateTime, server_default=func.now())

    __table_args__ = (
        Index('idx_minoquote_id', 'id'),
        UniqueConstraint('q', 'a', name='uq_minoquote_q_a')
    )

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
                
                insert_stmt = insert(MinoQuote).values(q=q_value, a=a_value, h=h_value)
                insert_stmt = insert_stmt.on_conflict_do_nothing(index_elements=['q', 'a'])
                connection.execute(insert_stmt)

            # 커넥션을 통해 커밋
            connection.commit()

    print("데이터 삽입 완료")

except Exception as e:
    print(f"오류 발생: {e}")
