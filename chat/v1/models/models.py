from sqlalchemy import create_engine, Column, Text, Integer, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import exc

Base = declarative_base()

class MinoQuote(Base):
    __tablename__ = 'MinoQuotes'
    id = Column(Integer, autoincrement=True)  # 자동 번호 생성
    q = Column(Text, primary_key=True)
    a = Column(Text, primary_key=True)
    h = Column(Text)
    reg_date = Column(DateTime, server_default=func.now())  # 저장일시
