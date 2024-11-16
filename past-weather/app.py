import os
from fastapi import FastAPI, APIRouter
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse, HTMLResponse
from starlette.requests import Request
from core.config import PREFIX, logging
from core.model import CustomTemplateResponse, RedirectGetResponse
from sqlalchemy import extract, func
from sqlalchemy.orm import sessionmaker
from database.create_tables import engine, MinoWeatherMonthly, MinoWeatherDaily
from database.weather_visualization import WeatherVisualization
from datetime import datetime
import calendar

app = FastAPI(title="Past Weather(송악읍)", version="0.0.1")
app.mount(f"{PREFIX}/static", StaticFiles(directory="static"), name="static")
router = APIRouter(prefix=PREFIX)
logger = logging.getLogger(__name__)
SessionLocal = sessionmaker(bind=engine)
CITY = 'songak'
MIN_YEAR = 2014

@router.get("/", response_class=RedirectResponse)
async def to_firstpage(request: Request):
    # use MinoWeatherMonthly, using SQLAlchemy
    # group by year, order by desc
    return CustomTemplateResponse("index.html", {"request": request})

@router.get("/{city:str}/{yyyy:str}", response_class=HTMLResponse)
async def monthly_chart(request: Request, city: str, yyyy: str):
    '''
    년-월별 차트 생성
    '''
    if not yyyy.isdigit():
        yyyy = datetime.now().year  
        return RedirectGetResponse(url=f"{PREFIX}/{city}/{yyyy}")

    current_year = datetime.now().year
    if MIN_YEAR > int(yyyy) or int(yyyy) > current_year:
        yyyy = current_year
        return RedirectGetResponse(url=f"{PREFIX}/{city}/{yyyy}")

    logger.info(f"city: {city}, yyyy: {yyyy}")

    session = SessionLocal()
    data = {
        '일자': [],
        '온도(°C)': [],
        '습도(%)': [],
        '강수량(mm)': [],
        '강수형태': []
    }

    try:
        query = session.query(MinoWeatherMonthly)\
            .filter(MinoWeatherMonthly.measure_month.like(f"{yyyy}%"))\
            .order_by(MinoWeatherMonthly.measure_month.asc())
        logger.debug(str(query))
        monthly_data = query.all()

        for entry in monthly_data:
            data['일자'].append(entry.measure_month)
            data['강수량(mm)'].append(int(entry.sum_precipitation))
            data['강수형태'].append(int(entry.precipitation_type))
            data['습도(%)'].append(int(entry.avg_humidity))
            data['온도(°C)'].append(int(entry.avg_temperature))

        # 클래스 인스턴스 생성
        weather_viz = WeatherVisualization(data)
        # 차트 생성
        combined_chart = weather_viz.combined_chart().to_html()

    except Exception as e:
        logger.error(f"Error occurred: {e}")
        return HTMLResponse(content="데이터를 가져오는 중 오류가 발생했습니다.", status_code=500)

    finally:
        session.close()

    title = f'송악읍 {yyyy}년 기상 정보'
    return CustomTemplateResponse("chart.html", {"request": request, "title": title, "chart": combined_chart})

@router.get("/{city:str}/{yyyy:str}/{mm:str}", response_class=HTMLResponse)
async def daily_chart(request: Request, city: str, yyyy: str, mm: str):
    '''
    일별 강수량, 일별 평균 온도 그래프
    '''
    session = SessionLocal()
    # 현재 년도 가져오기
    current_year = datetime.now().year

    # yyyy 검증 및 최대 월 가져오기
    if not str(yyyy).isdigit() or (MIN_YEAR > int(yyyy) or int(yyyy) > current_year):
        yyyy = current_year  # 유효하지 않으면 현재년도로 대체
        mm = get_max_month_for_year(session, yyyy)  # 최대 월 가져오기
        return get_redirect_url(city, yyyy, mm)

    # mm 검증 및 최대 월 가져오기
    if not str(mm).isdigit() or (1 > int(mm) or int(mm) > 12) or len(mm) > 2:
        mm = get_max_month_for_year(session, yyyy)  # 최대 월 가져오기
        return get_redirect_url(city, yyyy, mm)

    logger.info(f"city: {city}, yyyy: {yyyy}, mm: {mm}")

    data = {
        '일자': [],
        '온도(°C)': [],
        '습도(%)': [],
        '강수량(mm)': [],
        '강수형태': []
    }

    try:
        start_date = f"{yyyy}-{mm}-01"  # 시작일
        last_day = calendar.monthrange(int(yyyy), int(mm))[1]  # 해당 월의 마지막 날짜
        end_date = f"{yyyy}-{mm}-{last_day}"  # 종료일
        query = session.query(MinoWeatherDaily)\
            .filter(
                MinoWeatherDaily.measure_day >= start_date,
                MinoWeatherDaily.measure_day <= end_date
            )\
            .order_by(MinoWeatherDaily.measure_day.asc())
        logger.debug(str(query))
        daily_data = query.all()

        for entry in daily_data:
            data['일자'].append(entry.measure_day.strftime('%Y-%m-%d'))  # 날짜를 문자열로 변환
            data['강수량(mm)'].append(int(entry.sum_precipitation))
            data['강수형태'].append(int(entry.precipitation_type))
            data['습도(%)'].append(int(entry.avg_humidity))
            data['온도(°C)'].append(int(entry.avg_temperature))

        # 클래스 인스턴스 생성
        weather_viz = WeatherVisualization(data, 'daily')
        # 차트 생성
        combined_chart = weather_viz.combined_chart().to_html()

    except Exception as e:
        logger.error(f"Error occurred: {e}")
        return HTMLResponse(content="데이터를 가져오는 중 오류가 발생했습니다.", status_code=500)

    finally:
        session.close()

    title = f'송악읍 {yyyy}년 {mm}월 기상 정보'
    return CustomTemplateResponse("chart.html", {"request": request, "title": title, "chart": combined_chart})

def get_max_month_for_year(session, year):
    """주어진 년도의 최대 월을 반환하는 함수"""
    return session.query(
        func.max(extract('month', MinoWeatherDaily.measure_day)).label('max_month')
    ).filter(
        extract('year', MinoWeatherDaily.measure_day) == year
    ).scalar()

def get_redirect_url(city, yyyy, mm):
    """리다이렉트 URL 생성 함수"""
    return RedirectGetResponse(url=f"{PREFIX}/{city}/{yyyy}/{mm}")

app.include_router(router)  # 라우터 등록

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST")
    port = int(os.getenv("PORT"))
    uvicorn.run(app, host=host, port=port)