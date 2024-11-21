# %%
from core.config import logging
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import and_
from database.create_tables import engine, MinoWeatherDaily
import calendar
import pandas as pd

logger = logging.getLogger(__name__)
SessionLocal = sessionmaker(bind=engine)

def get_summary_by_month(loc_id: int, year: str, month: str):

    # 시작과 끝 날짜 계산
    start_date = f"{year}-{month}-01"
    last_day = calendar.monthrange(int(year), int(month))[1]  # 해당 월의 마지막 날짜
    end_date = f"{year}-{month}-{last_day}"

    query = (
        select(
            MinoWeatherDaily.measure_day,
            MinoWeatherDaily.max_temperature,
            MinoWeatherDaily.min_temperature,
            MinoWeatherDaily.max_humidity,
            MinoWeatherDaily.min_humidity,
            MinoWeatherDaily.sum_precipitation
        )
        .filter(
            and_(
                MinoWeatherDaily.loc_id == 1,
                MinoWeatherDaily.measure_day >= start_date,
                MinoWeatherDaily.measure_day <= end_date
            )
        )
    )

    session = SessionLocal()
    results = session.execute(query).fetchall()

    # 결과를 DataFrame으로 변환
    df = pd.DataFrame(results, columns=['measure_day', 'max_temperature', 'min_temperature', 'max_humidity', 'min_humidity', 'sum_precipitation'])

    # 강수량이 0인 경우 처리
    if df['sum_precipitation'].sum() == 0:
        summary = {
            'max_temperature': df['max_temperature'].max() if not df['max_temperature'].empty else None,
            'max_temperature_dates': df.loc[df['max_temperature'] == df['max_temperature'].max(), 'measure_day'].tolist(),
            'min_temperature': df['min_temperature'].min() if not df['min_temperature'].empty else None,
            'min_temperature_dates': df.loc[df['min_temperature'] == df['min_temperature'].min(), 'measure_day'].tolist(),
            'total_precipitation': 0,
            'max_precipitation': 0,
            'max_precipitation_dates': [],
        }
        return summary

    # 비가 한번이라도 온 경우
    summary = {
        'max_temperature': df['max_temperature'].max(),
        'max_temperature_dates': df.loc[df['max_temperature'] == df['max_temperature'].max(), 'measure_day'].tolist(),
        'min_temperature': df['min_temperature'].min(),
        'min_temperature_dates': df.loc[df['min_temperature'] == df['min_temperature'].min(), 'measure_day'].tolist(),
        'total_precipitation': df['sum_precipitation'].sum(),
        'max_precipitation': df['sum_precipitation'].max(),
        'max_precipitation_dates': df.loc[df['sum_precipitation'] == df['sum_precipitation'].max(), 'measure_day'].tolist(),
    }
    return summary

if __name__ == "__main__":
    summary = get_summary_by_month(1, "2023", "01")
    print(summary)


