from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey, create_engine, Index, UniqueConstraint, text, func,TIMESTAMP
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
    create_at = Column(TIMESTAMP, server_default=func.now())
    update_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

class MinoPrecipitationCode(Base):
    '''
    강수형태 : 없음(0), 비(1), 비/눈(2), 눈(3), 소나기(4), 빗방울(5), 빗방울눈날림(6), 눈날림(7) 
    '''
    __tablename__ = 'MinoPrecipitationCode'
    code = Column(Integer, primary_key=True)
    description = Column(String(255))
    create_at = Column(TIMESTAMP, server_default=func.now())
    update_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

class MinoWeatherHourly(Base):
    __tablename__ = 'MinoWeatherHourly'
    id = Column(Integer, primary_key=True, autoincrement=True)
    loc_id = Column(Integer, ForeignKey('MinoLocations.id'), nullable=False)
    measure_date = Column(DateTime, nullable=False, unique=True) # 날짜
    precipitation = Column(Float) # 강수
    precipitation_type = Column(Integer, ForeignKey('MinoPrecipitationCode.code'), nullable=False) # 강수형태
    temperature = Column(Float) # 온도
    humidity = Column(Float) # 습도
    create_at = Column(TIMESTAMP, server_default=func.now())
    update_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('ix_loc_id_measure_date', 'loc_id', 'measure_date'),  # loc_id와 measure_date에 대한 인덱스 추가
    )

    def __repr__(self):
        return (f"<MinoWeather(id={self.id}, loc_id={self.loc_id}, "
                f"measure_date={self.measure_date}, rainfall={self.precipitation}, "
                f"precipitation_type={self.precipitation_type}, temperature={self.temperature}, "
                f"humidity={self.humidity})>")

    def __hash__(self):
        # loc_id와 measure_date를 해시값으로 사용
        return hash((self.loc_id, self.measure_date))

    def __eq__(self, other):
        if isinstance(other, MinoWeatherHourly):
            # loc_id와 measure_date가 같으면 동일한 객체로 간주
            return (self.loc_id, self.measure_date) == (other.loc_id, other.measure_date)
        return False

class MinoWeatherDaily(Base):
    '''
    MinoWeatherHourly => MinoWeatherDaily
    '''
    __tablename__ = 'MinoWeatherDaily'
    id = Column(Integer, primary_key=True, autoincrement=True)
    loc_id = Column(Integer, ForeignKey('MinoLocations.id'), nullable=False)
    measure_day = Column(Date, nullable=False)  # 날짜 (년-월-일)
    sum_precipitation = Column(Float)  # 일일 강수량
    precipitation_type = Column(Integer, ForeignKey('MinoPrecipitationCode.code'), nullable=False) # 강수형태
    max_temperature = Column(Float)  # 최대 온도
    min_temperature = Column(Float)  # 최소 온도
    avg_temperature = Column(Float)  # 평균 온도
    max_humidity = Column(Float)  # 최대 습도
    min_humidity = Column(Float)  # 최소 습도
    avg_humidity = Column(Float)  # 평균 습도
    create_at = Column(TIMESTAMP, server_default=func.now())
    update_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('ix_loc_id_measure_day', 'loc_id', 'measure_day'),  # loc_id와 measure_day에 대한 인덱스 추가
        UniqueConstraint('loc_id', 'measure_day', name='uq_loc_id_measure_day')  # 고유 제약 조건 추가
    )

    def __repr__(self):
        return (f"<MinoWeatherDaily(id={self.id}, loc_id={self.loc_id}, "
                f"measure_day={self.measure_day}, daily_precipitation={self.daily_precipitation}, "
                f"precipitation_type={self.precipitation_type}, max_temperature={self.max_temperature}, "
                f"min_temperature={self.min_temperature}, avg_temperature={self.avg_temperature}, "
                f"max_humidity={self.max_humidity}, min_humidity={self.min_humidity}, "
                f"avg_humidity={self.avg_humidity})>")


class MinoWeatherWeekly(Base):
    '''
    MinoWeatherHourly => MinoWeatherWeekly
    '''
    __tablename__ = 'MinoWeatherWeekly'
    id = Column(Integer, primary_key=True, autoincrement=True)
    loc_id = Column(Integer, ForeignKey('MinoLocations.id'), nullable=False)
    measure_week = Column(String, nullable=False)  # 년-월-주 (예: '2024-11-2')
    sum_precipitation = Column(Float)  # 한주 강수량
    precipitation_type = Column(Integer, ForeignKey('MinoPrecipitationCode.code'), nullable=False) # 강수형태
    max_temperature = Column(Float)  # 최대 온도
    min_temperature = Column(Float)  # 최소 온도
    avg_temperature = Column(Float)  # 평균 온도
    max_humidity = Column(Float)  # 최대 습도
    min_humidity = Column(Float)  # 최소 습도
    avg_humidity = Column(Float)  # 평균 습도
    create_at = Column(TIMESTAMP, server_default=func.now())
    update_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('ix_loc_id_measure_week', 'loc_id', 'measure_week'),  # loc_id와 measure_week에 대한 인덱스 추가
        UniqueConstraint('loc_id', 'measure_week', name='uq_loc_id_measure_week')  # 고유 제약 조건 추가
    )

    def __repr__(self):
        return (f"<MinoWeatherWeekly(id={self.id}, loc_id={self.loc_id}, "
                f"measure_week={self.measure_week}, weekly_precipitation={self.weekly_precipitation}, "
                f"precipitation_type={self.precipitation_type}, max_temperature={self.max_temperature}, "
                f"min_temperature={self.min_temperature}, avg_temperature={self.avg_temperature}, "
                f"max_humidity={self.max_humidity}, min_humidity={self.min_humidity}, "
                f"avg_humidity={self.avg_humidity})>")

class MinoWeatherMonthly(Base):
    __tablename__ = 'MinoWeatherMonthly'
    id = Column(Integer, primary_key=True, autoincrement=True)
    loc_id = Column(Integer, ForeignKey('MinoLocations.id'), nullable=False)
    measure_month = Column(String, nullable=False)  # 년-월 (예: '2024-11')
    sum_precipitation = Column(Float)  # 월간 강수량
    precipitation_type = Column(Integer, ForeignKey('MinoPrecipitationCode.code'), nullable=False) # 강수형태
    max_temperature = Column(Float)  # 최대 온도
    min_temperature = Column(Float)  # 최소 온도
    avg_temperature = Column(Float)  # 평균 온도
    max_humidity = Column(Float)  # 최대 습도
    min_humidity = Column(Float)  # 최소 습도
    avg_humidity = Column(Float)  # 평균 습도
    create_at = Column(TIMESTAMP, server_default=func.now())
    update_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('ix_loc_id_measure_month', 'loc_id', 'measure_month'),  # loc_id와 measure_month에 대한 인덱스 추가
        UniqueConstraint('loc_id', 'measure_month', name='uq_loc_id_measure_month')  # 고유 제약 조건 추가
    )

    def __repr__(self):
        return (f"<MinoWeatherMonthly(id={self.id}, loc_id={self.loc_id}, "
                f"measure_month={self.measure_month}, monthly_precipitation={self.sum_precipitation}, "
                f"precipitation_type={self.precipitation_type}, max_temperature={self.max_temperature}, "
                f"min_temperature={self.min_temperature}, avg_temperature={self.avg_temperature}, "
                f"max_humidity={self.max_humidity}, min_humidity={self.min_humidity}, "
                f"avg_humidity={self.avg_humidity})>")



# SQLAlchemy 엔진 생성
DATABASE_URL='postgresql://ezsimple:qwer%21%4034@138.2.125.118:5432/ezsimple'
engine = create_engine(DATABASE_URL, echo=True)

# 세션 메이커 초기화
Session = sessionmaker(bind=engine)
session = Session()

# 테이블 생성
Base.metadata.create_all(engine)