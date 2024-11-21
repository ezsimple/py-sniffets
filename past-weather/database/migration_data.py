'''
송악읍
├── 송악읍2020
│   ├── 송악읍_강수_202001_202012.csv
│   ├── 송악읍_기온_202001_202012.csv
│   ├── 송악읍_습도_202001_202012.csv
│   └── 송악읍_강수형태_202001_202012.csv
├── 송악읍2021
│   ├── 송악읍_강수_202101_202112.csv
│   ├── 송악읍_기온_202101_202112.csv
│   ├── 송악읍_습도_202101_202112.csv
│   └── 송악읍_강수형태_202101_202112.csv
├── 송악읍2022
│   ├── 송악읍_강수_202201_202212.csv
│   ├── 송악읍_기온_202201_202212.csv
│   ├── 송악읍_습도_202201_202212.csv
│   └── 송악읍_강수형태_202201_202212.csv
├── 송악읍2023
│   ├── 송악읍_강수_202301_202312.csv
│   ├── 송악읍_기온_202301_202312.csv
│   ├── 송악읍_습도_202301_202312.csv
│   └── 송악읍_강수형태_202301_202312.csv
└── 송악읍2024
    ├── 송악읍_강수_202401_202410.csv
    ├── 송악읍_기온_202401_202410.csv
    ├── 송악읍_습도_202401_202410.csv
    └── 송악읍_강수형태_202401_202410.csv

송악읍2020 login ?7 ❯ head 송악읍_강수_202001_202012.csv
 format: day,hour,value location:55_112 Start : 20200101
 1, 0000, 0.000000

~/w/py-sniffets/pa/database/송악읍/송악읍2020 login ?7 ❯ head 송악읍_강수형태_202001_202012.csv
 format: day,hour,value location:55_112 Start : 20200101
 1, 0000, 0.000000

~/w/py-sniffets/pa/database/송악읍/송악읍2020 login ?7 ❯ head 송악읍_기온_202001_202012.csv
 format: day,hour,value location:55_112 Start : 20200101
 1, 0000, -0.200000

~/w/py-sniffets/pa/database/송악읍/송악읍2020 login ?7 ❯ head 송악읍_습도_202001_202012.csv
 format: day,hour,value location:55_112 Start : 20200101
 1, 0000, 81.000000

 각 폴더의 csv 파일을 읽어서, MinoWeatherHourly 테이블에 데이터를 넣고 싶어.
 데이터가 많은 만큼 yield 제너레이터를 사용했으면 해.
'''
# %%
import os
import csv
from create_tables import MinoWeatherHourly, MinoPrecipitationCode, session, engine
from datetime import datetime, timedelta
from sqlalchemy import text, MetaData, Table
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
import sys

START_YEAR=2014
END_YEAR=2024
LOC_ID=1 # 송악읍
DATA_DIR='송악읍'
MERGED_DIR='송악읍날씨정보'

def remove_blank_lines(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    # 마지막 공백 라인 제거
    while lines and lines[-1].strip() == '':
        lines.pop()
    
    # 수정된 내용을 다시 파일에 쓰기
    with open(file_path, 'w') as file:
        file.writelines(lines)

def remove_all_blank_lines(directory = f'./{DATA_DIR}'):
    for year in range(START_YEAR, END_YEAR + 1):
        year_dir = os.path.join(directory, f'{DATA_DIR}{year}')
        for filename in os.listdir(year_dir):
            if 'corrected_' in filename or 'merged_' in filename:
                continue
            if '강수' not in filename and '기온' not in filename and '습도' not in filename and '강수형태' not in filename:
                continue
            file_path = os.path.join(year_dir, filename) 
            remove_blank_lines(file_path)

def make_correct_csv_file(directory):
    for year in range(START_YEAR, END_YEAR + 1):
        weather_data = set()  # 중복을 방지하기 위한 set
        year_dir = os.path.join(directory, f'송악읍{year}')
        for filename in os.listdir(year_dir):
            if 'corrected_' in filename or 'merged_' in filename:
                continue
            if '강수' not in filename and '기온' not in filename and '습도' not in filename and '강수형태' in filename:
                continue

            file_path = os.path.join(year_dir, filename)

            with open(file_path, 'r') as file:
                lines = file.readlines()  # 파일의 모든 줄을 읽어옵니다.

            if len(lines) >= 1:
                first_line = lines[0].strip()
                if "Start :" in first_line: # 첫 번째 줄에서 "Start :" 부분을 찾습니다.
                    # "Start :"를 기준으로 나누고, 첫 번째 부분과 두 번째 부분을 구분합니다.
                    parts = first_line.split("Start :")
                    if len(parts) == 2:
                        # 수정된 첫 번째 줄과 두 번째 줄을 생성합니다.
                        modified_first_line = " " + parts[0].strip() + '\n'
                        modified_second_line = " Start : " + parts[1].strip() + '\n'
                        with open(file_path, 'w') as output_file: # 원본 파일에 덮어쓰기
                            output_file.write(modified_first_line)
                            output_file.write(modified_second_line)
                            output_file.writelines(lines[1:])  # 두 번째 줄부터 끝까지 복사

            with open(file_path, 'r') as file:
                reader = csv.reader(file)
                next(reader)  # 첫 번째 줄(헤더) 건너뛰기
                start_date = None
                corrected_data = []
                for row in reader:
                    if 'Start :' in row[0]:
                        start_date = row[0].split(': ')[1]  # Start 날짜 추출
                        start_year = int(start_date[:4])
                        start_month = int(start_date[4:6])
                        continue

                    day, hour, value = int(row[0]), int(row[1]), float(row[2])
                    # measure_date 생성
                    measure_date = datetime(
                        year=start_year,
                        month=start_month,
                        day=day,
                        hour=hour // 100,  # HHMM을 HH와 MM으로 나누기
                        minute=hour % 100,  # 분은 HHMM의 나머지
                        second=0  # 초는 0으로 설정
                    )

                    # measure_date => yyyy-mm-dd hh:mm:ss 형식으로 변환
                    # row[0] => yyyy-mm-dd hh:mm:ss, row[1] => value, row[2] => value 로 
                    formatted_date = measure_date.strftime('%Y-%m-%d %H:%M:%S')
                    corrected_data.append([formatted_date, value])  # 새로운 형식으로 데이터 추가
                    # 현재 csv 라인 변경 및 

            output_file_path = os.path.join(year_dir, f'corrected_{filename}')  # 수정된 파일 이름
            with open(output_file_path, 'w', newline='') as output_file:
                writer = csv.writer(output_file)
                writer.writerow(['measure_date', 'value'])  # 헤더 작성
                writer.writerows(corrected_data)  # 수정된 데이터 작성
                # 변경된 내용을 csv 파일에 저장

# CSV 파일을 읽어 MinoWeatherHourly 객체를 생성하는 제너레이터 함수
def make_pandas_weather_data(directory):
    output_dir = '송악읍날씨정보'
    os.makedirs(output_dir, exist_ok=True)
    for year in range(START_YEAR, END_YEAR + 1):
        weather_data = set()  # 중복을 방지하기 위한 set
        year_dir = os.path.join(directory, f'송악읍{year}')
        for filename in os.listdir(year_dir):
            if 'corrected_' not in filename:
                continue

            file_path = os.path.join(year_dir, filename)
            with open(file_path, 'r') as file:
                print(file_path)
                if '강수' in filename and '강수형태' not in filename:
                    precipitation_df = pd.read_csv(file_path, parse_dates=['measure_date'])
                    precipitation_df['precipitation'] = precipitation_df['value']
                    precipitation_df.drop('value', axis=1, inplace=True)
                if '기온' in filename:
                    temperature_df = pd.read_csv(file_path, parse_dates=['measure_date'])
                    temperature_df['temperature'] = temperature_df['value']
                    temperature_df.drop('value', axis=1, inplace=True)
                if '습도' in filename:
                    humidity_df = pd.read_csv(file_path, parse_dates=['measure_date'])
                    humidity_df['humidity'] = humidity_df['value']
                    humidity_df.drop('value', axis=1, inplace=True)
                if '강수형태' in filename:
                    precipitation_type_df = pd.read_csv(file_path, parse_dates=['measure_date'])
                    precipitation_type_df['precipitation_type'] = precipitation_type_df['value']
                    precipitation_type_df.drop('value', axis=1, inplace=True)

        merged_df = pd.merge(precipitation_df, temperature_df, on='measure_date', how='outer')
        merged_df = pd.merge(merged_df, humidity_df, on='measure_date', how='outer')
        merged_df = pd.merge(merged_df, precipitation_type_df, on='measure_date', how='outer')

        # 이상치 처리 - 강수량 precipitation이 음수인 경우 0으로 변경
        # 이상치 처리 - 강수형태 precipitation_type이 음수인 경우 0으로 변경
        merged_df['precipitation'] = merged_df['precipitation'].apply(lambda x: max(x, 0))
        merged_df['precipitation_type'] = merged_df['precipitation_type'].apply(lambda x: max(x, 0))

        # 이상치 처리 - 습도
        merged_df['humidity'] = merged_df['humidity'].apply(lambda x: max(x, 0))
        # 평균과 표준편차 계산
        mean_humidity = merged_df['humidity'].mean()
        std_dev_humidity = merged_df['humidity'].std()

        # 하한과 상한 설정
        lower_bound = mean_humidity - 2 * std_dev_humidity
        upper_bound = mean_humidity + 2 * std_dev_humidity

        # 이상치 보정
        merged_df['humidity'] = merged_df['humidity'].apply(lambda x: max(min(x, upper_bound), lower_bound))

        # 이상치 처리 - 온도: 영하 -20는 0으로 처리
        # 영하 -20도 이하의 온도 값을 0으로 처리하여 이상치를 제거합니다.
        # 나머지 온도 값은 그대로 유지됩니다.
        # merged_df['temperature'] = merged_df['temperature'].add(20).apply(lambda x: max(x, 0)).sub(20)

        mean_temperature = merged_df['temperature'].mean()
        std_dev_temperature = merged_df['temperature'].std()

        # 하한과 상한 설정
        lower_temp_bound = mean_temperature - 2 * std_dev_temperature
        upper_temp_bound = mean_temperature + 2 * std_dev_temperature

        # 이상치 보정
        merged_df['temperature'] = merged_df['temperature'].apply(lambda x: max(min(x, upper_temp_bound), lower_temp_bound))

        merged_df['loc_id'] = LOC_ID
        # 결측치 처리
        merged_df.fillna(0, inplace=True)
        
        merged_filename = f'merged_송악읍{year}.csv'
        merged_df.to_csv(os.path.join(output_dir, merged_filename), index=False)

# read_weather_data 제너레이터 함수 정의
def read_weather_data(directory):
    for year in range(START_YEAR, END_YEAR + 1):
        filename = f'merged_송악읍{year}.csv'
        file_path = os.path.join(directory, filename)
        
        print(file_path)
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            for index, row in df.iterrows():
                yield MinoWeatherHourly(
                    measure_date=row['measure_date'],
                    loc_id=LOC_ID, # 송악읍
                    precipitation=row['precipitation'],
                    temperature=row['temperature'],
                    humidity=row['humidity'],
                    precipitation_type=row['precipitation_type']
                )


def save_to_mino_weather_table(directory):
    # 메타데이터 객체 생성
    metadata = MetaData(schema='public')

    # 테이블 정의
    MinoWeatherHourly = Table('MinoWeatherHourly', metadata, autoload_with=engine)
    MinoWeatherDaily = Table('MinoWeatherDaily', metadata, autoload_with=engine)
    MinoWeatherWeekly = Table('MinoWeatherWeekly', metadata, autoload_with=engine)
    MinoWeatherMonthly = Table('MinoWeatherMonthly', metadata, autoload_with=engine)

    # 1. 임시테이블 생성
    try:
        session.execute(text("""
            CREATE TEMPORARY TABLE temp_table (
                id serial4 NOT NULL,
                loc_id int4 NOT NULL,
                measure_date timestamp NOT NULL,
                precipitation float8 NULL,
                precipitation_type float8 NULL,
                temperature float8 NULL,
                humidity float8 NULL,
                create_at timestamp DEFAULT CURRENT_TIMESTAMP,
                update_at timestamp DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT "MinoWeatherHourly_measure_date_key" UNIQUE (measure_date),
                CONSTRAINT "MinoWeatherHourly_pkey" PRIMARY KEY (id)          
            )
        """))
        session.commit()
    except Exception as e:
        print(f"Error occurred: {e}")
    
    # 2. pandas로 temp_table 에 넣기
    # pandas.to_sql을 이용해서, 고속 저장
    with engine.connect() as connection:
        for year in range(START_YEAR, END_YEAR + 1):
            filename = f'merged_송악읍{year}.csv'
            file_path = os.path.join(directory, filename)
            current_time = datetime.now()
            print(file_path)
            if os.path.exists(file_path):
                df = pd.read_csv(file_path)
                df['create_at'] = current_time
                df['update_at'] = current_time
                df.to_sql('temp_table', connection, if_exists='append', index=False)
        connection.execute(text('VACUUM;'))

    # 3. temp 테이블의 데이터를 MinoWeatherHourly 테이블로 복사
    try:
        session.execute(text("""
            INSERT INTO public."MinoWeatherHourly" (measure_date, loc_id, precipitation, precipitation_type, temperature, humidity, create_at, update_at)
            SELECT measure_date, loc_id, precipitation, precipitation_type, temperature, humidity, create_at, update_at
            FROM temp_table
            ON CONFLICT (measure_date) DO NOTHING;
        """))

        session.execute(text("""
            INSERT INTO public."MinoWeatherDaily" (loc_id, measure_day, sum_precipitation, precipitation_type,
                                max_temperature, min_temperature, avg_temperature,
                                max_humidity, min_humidity, avg_humidity, create_at, update_at)
            SELECT
                loc_id,
                measure_date::date AS measure_day,  -- measure_date를 날짜 형식으로 변환
                SUM(precipitation) AS sum_precipitation,  -- 일일 강수량 합계
                MAX(precipitation_type) AS precipitation_type,  -- 눈, 비 구분을 위해
                MAX(temperature) AS max_temperature,  -- 최대 온도
                MIN(temperature) AS min_temperature,  -- 최소 온도
                AVG(temperature) AS avg_temperature,  -- 평균 온도
                MAX(humidity) AS max_humidity,  -- 최대 습도
                MIN(humidity) AS min_humidity,  -- 최소 습도
                AVG(humidity) AS avg_humidity,  -- 평균 습도
                NOW() AS create_at,  -- 현재 시간
                NOW() AS update_at   -- 현재 시간
            FROM
                public."MinoWeatherHourly" AS main
            GROUP BY
                loc_id, measure_date::date  -- loc_id와 날짜로 그룹화
            ON CONFLICT (loc_id, measure_day) DO NOTHING;
        """))

        session.execute(text("""
            INSERT INTO public."MinoWeatherWeekly" (loc_id, measure_week, sum_precipitation, precipitation_type, 
                                max_temperature, min_temperature, avg_temperature, 
                                max_humidity, min_humidity, avg_humidity, create_at, update_at)
            SELECT 
                loc_id,
                TO_CHAR(DATE_TRUNC('month', measure_date), 'YYYY-MM') || '-' || 
                LPAD(CASE 
                    WHEN EXTRACT(WEEK FROM measure_date) - EXTRACT(WEEK FROM DATE_TRUNC('month', measure_date)) + 1 = 1 THEN '01'
                    WHEN EXTRACT(WEEK FROM measure_date) - EXTRACT(WEEK FROM DATE_TRUNC('month', measure_date)) + 1 = 2 THEN '02'
                    WHEN EXTRACT(WEEK FROM measure_date) - EXTRACT(WEEK FROM DATE_TRUNC('month', measure_date)) + 1 = 3 THEN '03'
                    WHEN EXTRACT(WEEK FROM measure_date) - EXTRACT(WEEK FROM DATE_TRUNC('month', measure_date)) + 1 = 4 THEN '04'
                    ELSE '05'  -- 다섯째주 이상인 경우
                END, 2, '0') AS measure_week,  -- 주를 "yyyy-mm-01" 형식으로 표현
                SUM(precipitation) AS sum_precipitation,  -- 주간 강수량 합계
                MAX(precipitation_type) AS precipitation_type,  -- 눈,비 구분을 위해
                MAX(temperature) AS max_temperature,  -- 주간 최대 온도
                MIN(temperature) AS min_temperature,  -- 주간 최소 온도
                AVG(temperature) AS avg_temperature,  -- 주간 평균 온도
                MAX(humidity) AS max_humidity,  -- 주간 최대 습도
                MIN(humidity) AS min_humidity,  -- 주간 최소 습도
                AVG(humidity) AS avg_humidity,  -- 주간 평균 습도
                NOW() AS create_at,  -- 현재 시간
                NOW() AS update_at   -- 현재 시간
            FROM 
                public."MinoWeatherHourly" AS main
            GROUP BY 
                loc_id, DATE_TRUNC('month', measure_date), 
                EXTRACT(WEEK FROM measure_date) - EXTRACT(WEEK FROM DATE_TRUNC('month', measure_date)) + 1  -- 주 번호를 그룹화
            ON CONFLICT (loc_id, measure_week) DO NOTHING;
        """))

        session.execute(text("""
            INSERT INTO public."MinoWeatherMonthly"
            (loc_id, measure_month, sum_precipitation, precipitation_type, max_temperature, min_temperature, avg_temperature, max_humidity, min_humidity, avg_humidity)
            SELECT 
                loc_id,
                TO_CHAR(measure_date, 'YYYY-MM') AS measure_month,
                SUM(precipitation) AS sum_precipitation,
                MAX(precipitation_type) AS precipitation_type, -- 눈, 비를 구분하기 위해.
                MAX(temperature) AS max_temperature,
                MIN(temperature) AS min_temperature,
                AVG(temperature) AS avg_temperature,
                MAX(humidity) AS max_humidity,
                MIN(humidity) AS min_humidity,
                AVG(humidity) AS avg_humidity
            FROM public."MinoWeatherHourly" AS main
            GROUP BY loc_id, TO_CHAR(measure_date, 'YYYY-MM')
            ON CONFLICT (loc_id, measure_month) DO NOTHING;
        """))

    except SQLAlchemyError as e:
        session.rollback()  # 트랜잭션 롤백
        print(f"Error inserting data: {e}")
        sys.exit(-1)

    # 4. temp 테이블 삭제
    session.execute(text(""" DROP TABLE IF EXISTS temp_table; """))

    # 5. 변경사항 커밋
    session.commit()


if __name__ == "__main__":
    directory = './송악읍'
    remove_all_blank_lines(directory)
    make_correct_csv_file(directory)
    make_pandas_weather_data(directory)
    save_to_mino_weather_table(directory='./송악읍날씨정보')
