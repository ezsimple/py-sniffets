from sqlalchemy import create_engine, Column, Text, Integer, DateTime, func, Sequence, Index, UniqueConstraint 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import exc

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