from sqlalchemy import create_engine, Column, Text, Integer, DateTime, func, Sequence, Index, UniqueConstraint, String
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

'''
Text(length=255): q와 a의 길이를 255자로 제한하여 인덱스 크기를 줄였습니다. 필요에 따라 이 값을 조정할 수 있습니다.
해시 인덱스: func.md5(q + a)를 사용하여 q와 a의 조합에 대한 해시 인덱스를 생성했습니다. 이렇게 하면 긴 문자열 대신 해시 값을 인덱싱하여 인덱스 크기를 줄일 수 있습니다.
이 구조로 테이블을 설계하면, id를 기반으로 효율적으로 조회할 수 있으며, q와 a의 조합에 대한 유일성도 보장됩니다. 인덱스 크기 문제를 피하면서 성능을 최적화할 수 있습니다.
'''
class MinoQuote2(Base):
    __tablename__ = 'MinoQuotes2'
    
    id = Column(Integer, Sequence('minoquote2_id_seq'), primary_key=True, nullable=False)  # 자동 번호 생성 및 유일성 보장
    q = Column(String(length=1024), nullable=False)  # 명언
    a = Column(String(length=32), nullable=False)   # 저자, 길이를 제한
    t = Column(String(length=16))  
    reg_date = Column(DateTime, server_default=func.now())  # 저장일시

    __table_args__ = (
        UniqueConstraint('q', 'a', name='uq_minoquote2_q_a'),  # q, a에 유일 제약 조건 추가
        Index('idx_minoquote2_hash', func.md5(q + a))  # q와 a의 해시를 사용한 인덱스
    )