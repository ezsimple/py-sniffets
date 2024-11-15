import os
from fastapi import FastAPI, APIRouter
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse, HTMLResponse
from starlette.requests import Request
from datetime import datetime
from core.config import PREFIX, logging
from core.model import CustomTemplateResponse
from sqlalchemy.orm import sessionmaker
from database.create_tables import engine, MinoWeatherMonthly, MinoWeatherDaily
import pandas as pd
import altair as alt

app = FastAPI(title="Past Weather(송악읍)", version="0.0.1")
app.mount("/past-weather/static", StaticFiles(directory="static"), name="static")
router = APIRouter(prefix=PREFIX)
logger = logging.getLogger(__name__)
SessionLocal = sessionmaker(bind=engine)
CITY = 'songak'

@router.get("/", response_class=RedirectResponse)
async def to_firstpage(request: Request):
    # use MinoWeatherMonthly, using SQLAlchemy
    # group by year, order by desc
    return CustomTemplateResponse("index.html", {"request": request})

@router.get("/{city:str}/{yyyy:str}", response_class=HTMLResponse)
async def year_chart(request: Request, city: str, yyyy: str):
    logger.info(f"city: {city}, yyyy: {yyyy}")

    session = SessionLocal()
    try:
        query = session.query(MinoWeatherMonthly)\
            .filter(MinoWeatherMonthly.measure_month.like(f"{yyyy}%"))\
            .order_by(MinoWeatherMonthly.measure_month.asc())
        # logger.debug(str(query))
        monthly_data = query.all()
        session.close()
    except Exception as e:
        logger.error(e)
    finally:
        session.close()

    data = {
        'month': [],
        'precipitation': [],
        'humidity': [],
        'temperature': []
    }

    for entry in monthly_data:
        data['month'].append(entry.measure_month)
        data['precipitation'].append(int(entry.sum_precipitation))
        data['humidity'].append(int(entry.avg_humidity))
        data['temperature'].append(int(entry.avg_temperature))
    
    df = pd.DataFrame(data)
    df['month'] = pd.to_datetime(df['month'], format='%Y-%m')

     # Altair 차트 생성
    daily_precipitation_chart = alt.Chart(df).mark_bar(color='green').encode(
        x='일:T',
        y='강수량:Q',
        tooltip=['일:T', '강수량:Q']
    ).properties(title='일별 강수량 변화')

    daily_temperature_chart = alt.Chart(df).mark_line(color='orange').encode(
        x='일:T',
        y='평균 온도:Q',
        tooltip=['일:T', '평균 온도:Q']
    ).properties(title='일별 평균 온도 변화')

    combined_chart = alt.vconcat(daily_precipitation_chart, daily_temperature_chart)

    return CustomTemplateResponse("year.html", {"request": request, "chart": combined_chart.to_html()})

@router.get("/{city:str}/{yyyy:str}/{mm:str}", response_class=HTMLResponse)
async def month_chart(request: Request, city: str, yyyy: str, mm: str):
    logger.info(f"city: {city}, yyyy: {yyyy}, mm: {mm}")
    return CustomTemplateResponse("month.html", {"request": request})

app.include_router(router)  # 라우터 등록

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST")
    port = int(os.getenv("PORT"))
    uvicorn.run(app, host=host, port=port)