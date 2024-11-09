from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# SQLAlchemy Base 클래스 정의
Base = declarative_base()

class MinoLocations(Base):
    __tablename__ = 'MinoLocations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    kor_name = Column(String(255)) # 한글 지역명
    eng_name = Column(String(255)) # 영문 지역명
    short_name = Column(String(255), unique=True) # 지역 약어
    latitude = Column(Float) # 위도
    longitude = Column(Float) # 경도
    timezone = Column(String(30), default='Asia/Seoul') # 시간대
    create_at = Column(DateTime, default=datetime.now()) # 생성 시간
    update_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now()) # 업데이트 시간

class MinoWeather(Base):
    __tablename__ = 'MinoWeather'

    id = Column(Integer, primary_key=True, autoincrement=True)
    loc_id = Column(Integer, ForeignKey('MinoLocations.id'))
    measure_date = Column(DateTime, nullable=False, unique=True) # 날짜
    precipitation = Column(Float) # 강수
    precip_type = Column(Float) # 강수형태
    temperature = Column(Float) # 온도
    humidity = Column(Float) # 습도
    create_at = Column(DateTime, default=datetime.now()) # 생성 시간
    update_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now()) # 업데이트 시간

    def __repr__(self):
        return (f"<MinoWeather(id={self.id}, loc_id={self.loc_id}, "
                f"measure_date={self.measure_date}, precipitation={self.precipitation}, "
                f"precip_type={self.precip_type}, temperature={self.temperature}, "
                f"humidity={self.humidity})>")

    def __hash__(self):
        # loc_id와 measure_date를 해시값으로 사용
        return hash((self.loc_id, self.measure_date))

    def __eq__(self, other):
        if isinstance(other, MinoWeather):
            # loc_id와 measure_date가 같으면 동일한 객체로 간주
            return (self.loc_id, self.measure_date) == (other.loc_id, other.measure_date)
        return False


# SQLAlchemy 엔진 생성
DATABASE_URL='postgresql://ezsimple:qwer%21%4034@138.2.125.118:5432/ezsimple'
engine = create_engine(DATABASE_URL, echo=True)

# 세션 메이커 초기화
Session = sessionmaker(bind=engine)
session = Session()

# 테이블 생성
Base.metadata.create_all(engine)
