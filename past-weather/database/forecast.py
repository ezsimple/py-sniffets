# 2024-12-01 부터 1시간 단위로 기상예보 데이터 수상
'''
Req:
http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst

params:
serviceKey=clzRha7FjiQHb9pLNqKTq1ieuSzvgbh%2BgIOGlrwUxQsVVk%2BfSJD5n5Ggu0YO3RDZEQowJ6eVgvZ65Hrw1C%2F%2BFw%3D%3D
numOfRows=100
pageNo=1
dataType=JSON
base_date=20241224
base_time=0000
nx=61
ny=09

Res:
numOfRows	한 페이지 결과 수
pageNo	페이지 번호
totalCount	데이터 총 개수
resultCode	응답메시지 코드
resultMsg	응답메시지 내용
dataType	데이터 타입
baseDate	발표일자
baseTime	발표시각
nx	예보지점 X 좌표
ny	예보지점 Y 좌표
category	자료구분코드
obsrValue	실황 값

T1H	기온
RN1	1시간 강수량
UUU	동서바람성분
VVV	남북바람성분
REH	습도
PTY	강수형태
VEC	풍향
WSD	풍속
'''
# %%
def fetch_weather_data():
    import requests
    import time
    import json
    from datetime import datetime, timedelta
    import os

    # Constants
    SERVICE_KEY = 'clzRha7FjiQHb9pLNqKTq1ieuSzvgbh+gIOGlrwUxQsVVk+fSJD5n5Ggu0YO3RDZEQowJ6eVgvZ65Hrw1C/+Fw=='

    # getUltraSrtNcst 초단기실황조회 X
    # getUltraSrtFcst 초단기예보조회 O 단 현재기준으로 하루전 데이터만 조회가능
    # getVilageFcst   단기예보조회   X
    # getFcstVersion  예보버전조회   X
    BASE_URL = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtFcst'
    # 송악읍
    NX = 61
    NY = 9

    # Start and end times
    start_time = datetime.now().date()
    end_time = start_time + timedelta(days=1)
    save_file = 'forecast_' + start_time.strftime('%Y%m%d') + '.csv'
    baseTime = start_time

    current_time = start_time
    while current_time <= end_time:
        # Prepare parameters
        params = {
            'serviceKey': SERVICE_KEY,
            'numOfRows': 100,
            'pageNo': 1,
            'dataType': 'JSON',
            'base_date': current_time.strftime('%Y%m%d'),
            'base_time': current_time.strftime('%H%M'),
            'nx': NX,
            'ny': NY
        }

        # Log the parameters being sent
        print(f'Parameters: {params}')  # Log request parameters

        # Make the API request
        response = requests.get(BASE_URL, params=params)
        # print(f'Response Code: {response.status_code}')  # Log response code
        # print(f'Response Content: {response.text}')  # Log response content
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2))

            # Initialize baseTime and create a dictionary to hold the final values
            final_values = {}

            for item in data['response']['body']['items']['item']:
                # Only process items that match the current baseTime
                if item['baseTime'] == baseTime.strftime('%H%M'):
                    # Store the last values for each category
                    final_values[item['baseTime']] = final_values.get(item['baseTime'], {'PTY': '', 'RN1': '', 'T1H': '', 'REH': ''})
                    if item['category'] == 'PTY':
                        final_values[item['baseTime']]['PTY'] = item['fcstValue']
                    elif item['category'] == 'RN1':
                        final_values[item['baseTime']]['RN1'] = item['fcstValue']
                    elif item['category'] == 'T1H':
                        final_values[item['baseTime']]['T1H'] = item['fcstValue']
                    elif item['category'] == 'REH':
                        final_values[item['baseTime']]['REH'] = item['fcstValue']


            # Write the final values to the CSV file
            with open(save_file, 'a') as f:
                for baseTime_key, values in final_values.items():
                    f.write(f"{start_time.strftime('%Y%m%d')}, {baseTime_key}, {values['PTY']}, {values['RN1']}, {values['T1H']}, {values['REH']}\n")

            time.sleep(1) # <= 200ms 를 기다렸으면해
            current_time += timedelta(hours=1)
            baseTime = current_time + timedelta(minutes=30) # current
            continue

        print(f'#ERROR#: {response.status_code}')  # Handle errors
        break

if __name__ == '__main__':
    fetch_weather_data()
