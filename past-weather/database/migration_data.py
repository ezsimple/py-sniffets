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

 각 폴더의 csv 파일을 읽어서, MinoWeather 테이블에 데이터를 넣고 싶어.
 데이터가 많은 만큼 yield 제너레이터를 사용했으면 해.
'''
# %%
import os
import csv
from create_tables import MinoWeather, session
from datetime import datetime, timedelta

def remove_blank_lines(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    # 마지막 공백 라인 제거
    while lines and lines[-1].strip() == '':
        lines.pop()
    
    # 수정된 내용을 다시 파일에 쓰기
    with open(file_path, 'w') as file:
        file.writelines(lines)

def remove_all_blank_lines(directory = './송악읍'):
    for year in range(2020, 2025):  # 2020년부터 2024년까지
        year_dir = os.path.join(directory, f'송악읍{year}')
        for filename in os.listdir(year_dir):
            if '강수' in filename or '기온' in filename or '습도' in filename or '강수형태' in filename:
                file_path = os.path.join(year_dir, filename) 
                remove_blank_lines(file_path)

def validate_csv_files(directory):
    for year in range(2020, 2025):  # 2020년부터 2024년까지
        year_dir = os.path.join(directory, f'송악읍{year}')
        for filename in os.listdir(year_dir):
            if '강수' in filename or '기온' in filename or '습도' in filename or '강수형태' in filename:
                file_path = os.path.join(year_dir, filename)
                with open(file_path, 'r') as file:
                    reader = csv.reader(file)
                    next(reader)  # 첫 번째 줄(헤더) 건너뛰기
                    for line_number, row in enumerate(reader, start=1):
                        try:
                            for row in reader:
                                if row[0].__contains__('Start :'):
                                    start_date = row[0].split(': ')[1]  # Start 날짜 추출
                                    start_year = int(start_date[:4])
                                    start_month = int(start_date[4:6])
                                else:
                                    day, hour, value = int(row[0]), int(row[1]), float(row[2])
                                    # 데이터에 따라 MinoWeather 객체 생성
                                    if '강수' in filename:
                                        precip_value = value
                                        precip_type = None  # 강수형태는 다른 파일에서 가져와야 함
                                    elif '기온' in filename:
                                        temperature = value
                                    elif '습도' in filename:
                                        humidity = value
                                    elif '강수형태' in filename:
                                        precip_type = value
                        except ValueError as e:
                            print(f"Error processing file {file_path}: Line {line_number} - {e}")
                            continue

# CSV 파일을 읽어 MinoWeather 객체를 생성하는 제너레이터 함수
def read_weather_data(directory):

    for year in range(2020, 2025):  # 2020년부터 2024년까지
        weather_data = set()  # 중복을 방지하기 위한 set
        year_dir = os.path.join(directory, f'송악읍{year}')
        for filename in os.listdir(year_dir):
            if '강수' in filename or '기온' in filename or '습도' in filename or '강수형태' in filename:
                file_path = os.path.join(year_dir, filename)
                with open(file_path, 'r') as file:
                    reader = csv.reader(file)
                    next(reader)  # 첫 번째 줄(헤더) 건너뛰기
                    start_date = None

                    try:
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

                            # MinoWeather 객체 생성
                            weather_record = MinoWeather(
                                id=None,
                                loc_id=1,  # 송악읍의 loc_id를 적절히 설정해야 함
                                measure_date=measure_date,
                                precipitation=0,
                                precip_type=None,
                                temperature=None,
                                humidity=None
                            )

                            # 데이터 업데이트
                            if '강수' in filename and '강수형태' not in filename:
                                weather_record.precipitation = value
                            elif '기온' in filename:
                                weather_record.temperature = value
                            elif '습도' in filename:
                                weather_record.humidity = value
                            elif '강수형태' in filename:
                                weather_record.precip_type = value

                            # set에 추가 (중복된 경우 자동으로 무시됨)
                            weather_data.add(weather_record)

                            # 모든 데이터가 준비되면 출력
                    except ValueError as e:
                        print(f"Error processing file {file_path}: {e}")
                        continue

        for record in weather_data:
            print(record)


def insert_weather_data(session, directory):
    for weather_data in read_weather_data(directory):
        session.add(weather_data)
        if session.new and len(session.new) >= 1000:  # 1000개마다 커밋
            session.commit()
    session.commit()  # 남은 데이터 커밋

if __name__ == "__main__":
    directory = './송악읍'
    remove_all_blank_lines(directory)
    validate_csv_files(directory)
    read_weather_data(directory)
    # insert_weather_data(session, directory)

# %%
