import os
from fastapi import FastAPI, APIRouter
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse, HTMLResponse, JSONResponse
from starlette.requests import Request
from core.config import PREFIX, logging
from core.model import CustomTemplateResponse, RedirectGetResponse
from sqlalchemy import extract, func
from sqlalchemy.orm import sessionmaker
from database.create_tables import engine, MinoWeatherMonthly, MinoWeatherDaily
from database.weather_visualization import WeatherVisualization
from datetime import datetime
import calendar
import json

app = FastAPI(title="Past Weather(송악읍)", version="0.0.1")
app.mount(f"{PREFIX}/static", StaticFiles(directory="static"), name="static")
router = APIRouter(prefix=PREFIX)
logger = logging.getLogger(__name__)
SessionLocal = sessionmaker(bind=engine)
CITY = 'songak'
MIN_YEAR = 2014

@router.get("/", response_class=RedirectResponse)
async def to_firstpage(request: Request):
    city = CITY
    yyyy = datetime.now().year
    mm = get_max_month_for_year(yyyy)
    return get_redirect_url(city, yyyy, mm)

@router.get("/api/{city:str}/{yyyy:str}", response_class=JSONResponse)
async def monthly_api(request: Request, city: str, yyyy: str):
    '''
    년-월별 차트 생성
    '''
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

    except Exception as e:
        logger.error(f"Error occurred: {e}")
        return JSONResponse(content={"error": f"Internal server error: {str(e)}"}, status_code=500)

    finally:
        session.close()
    
    return JSONResponse(content=data)

@router.get("/api/{city:str}/{yyyy:str}/{mm:str}", response_class=JSONResponse)
async def daily_api(request: Request, city: str, yyyy: str, mm: str):
    '''
    일별 강수량, 일별 평균 온도 그래프
    '''
    logger.info(f"city: {city}, yyyy: {yyyy}, mm: {mm}")

    session = SessionLocal()
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

    except Exception as e:
        logger.error(f"Error occurred: {e}")
        return JSONResponse(content={"error": f"Internal server error: {str(e)}"}, status_code=500)

    finally:
        session.close()
    
    return JSONResponse(content=data)

@router.get("/{city:str}/{yyyy:str}", response_class=HTMLResponse)
async def monthly_chart(request: Request, city: str, yyyy: str):
    current_year = datetime.now().year
    if not str(yyyy).isdigit() or (MIN_YEAR > int(yyyy) or int(yyyy) > current_year):
        yyyy = current_year  # 유효하지 않으면 현재년도로 대체
        return get_redirect_url(city, yyyy, None)

    json_data = await monthly_api(request, city, yyyy)
    data = json_data.body.decode('utf-8')
    data = json.loads(data)
    weather_viz = WeatherVisualization(data)
    combined_chart = weather_viz.combined_chart().to_json()

    min_month, max_month = get_min_max_month()
    years = calculate_year_difference(min_month, max_month)
    months = get_months_for_year(yyyy)
    selectedMonth = yyyy + '-' + months[-1]
    title = f'송악읍 과거 날씨 정보'
    return CustomTemplateResponse("chart.html", {"request": request, "title": title, "chart": combined_chart, "selectedMonth": selectedMonth, "min_month": min_month, "max_month": max_month, "years":years })

@router.get("/{city:str}/{yyyy:str}/{mm:str}", response_class=HTMLResponse)
async def daily_chart(request: Request, city: str, yyyy: str, mm: str):
    # 현재 년도 가져오기
    selectedMonth = yyyy + '-' + mm
    min_month, max_month = get_min_max_month()
    years = calculate_year_difference(min_month, max_month)
    current_year = datetime.now().year

    # 제공가능한 날짜 범위를 벗어나는 경우
    if min_month > selectedMonth or max_month < selectedMonth:
        yyyy = current_year  # 유효하지 않으면 현재년도로 대체
        mm = get_max_month_for_year(yyyy)  # 최대 월 가져오기
        return get_redirect_url(city, yyyy, mm)

    # yyyy 검증 및 최대 월 가져오기
    if not str(yyyy).isdigit() or (MIN_YEAR > int(yyyy) or int(yyyy) > current_year):
        yyyy = current_year  # 유효하지 않으면 현재년도로 대체
        mm = get_max_month_for_year(yyyy)  # 최대 월 가져오기
        return get_redirect_url(city, yyyy, mm)

    # mm 검증 및 최대 월 가져오기
    if not str(mm).isdigit() or (1 > int(mm) or int(mm) > 12) or len(mm) > 2:
        mm = get_max_month_for_year(yyyy)  # 최대 월 가져오기
        return get_redirect_url(city, yyyy, mm)

    json_data = await daily_api(request, city, yyyy, mm)
    data = json_data.body.decode('utf-8')
    data = json.loads(data)
    weather_viz = WeatherVisualization(data, 'daily')
    combined_chart = weather_viz.combined_chart().to_json()

    title = f'송악읍 과거 날씨 정보'
    return CustomTemplateResponse("chart.html", {"request": request, "title": title, "chart": combined_chart, "selectedMonth": selectedMonth, "min_month": min_month, "max_month": max_month, "years": years})


def get_years():
    """데이터베이스에 존재하는 모든 연도를 반환하는 함수"""
    session = SessionLocal()
    try:
        result = session.query(MinoWeatherMonthly.measure_month).distinct().all()
        years = sorted(set(month[0].split('-')[0] for month in result))  # 중복 제거 후 정렬
        return years
    finally:
        session.close()


def get_min_max_month():
    """month picker min max range """
    session = SessionLocal()
    try:
        result = session.query(
            func.min(MinoWeatherMonthly.measure_month).label('min_month'),
            func.max(MinoWeatherMonthly.measure_month).label('max_month')
        ).one()
        return result.min_month, result.max_month  # max_month와 min_month 반환
    finally:
        session.close()

def calculate_year_difference(min_month, max_month):
    min_date = datetime.strptime(min_month, '%Y-%m')
    max_date = datetime.strptime(max_month, '%Y-%m')
    year_difference = max_date.year - min_date.year
    if max_date.month < min_date.month:
        year_difference -= 1
    return year_difference

def get_months_for_year(year):
    """주어진 년도의 최대 월을 반환하는 함수"""
    session = SessionLocal()
    try:
        # 주어진 연도에 해당하는 월을 선택하는 쿼리
        result = session.query(MinoWeatherMonthly.measure_month).filter(
            MinoWeatherMonthly.measure_month.like(f'{year}-%')
        ).distinct().order_by(MinoWeatherMonthly.measure_month.asc()).all()

        months = [month[0].split('-')[1] for month in result]
        return months
    finally:
        session.close()

def get_max_month_for_year(year):
    """주어진 년도의 최대 월을 반환하는 함수"""
    session = SessionLocal()
    try:
        return session.query(
            func.max(extract('month', MinoWeatherDaily.measure_day)).label('max_month')
        ).filter(
            extract('year', MinoWeatherDaily.measure_day) == year
        ).scalar()
    finally:
        session.close()

def get_redirect_url(city, yyyy, mm):
    """리다이렉트 URL 생성 함수"""
    url = f'{PREFIX}/{city}/{yyyy}'
    if mm:
        url = f'{PREFIX}/{city}/{yyyy}/{mm:02}'
    return RedirectGetResponse(url=url)

app.include_router(router)  # 라우터 등록

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST")
    port = int(os.getenv("PORT"))
    uvicorn.run(app, host=host, port=port)