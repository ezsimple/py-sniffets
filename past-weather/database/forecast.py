# %%
def generate_csv_row(base_time, data):
    try:
        items = data['response']['body']['items']['item']
        base_date = items[0]['baseDate'] 
    except:
        return ''

    final_values = {}


    for item in items:
      # Store the last values for each category
      category = item['category']

      final_values.setdefault(item['baseTime'], {'PTY': '', 'RN1': '', 'T1H': '', 'REH': ''})[category] = {
          'PTY': lambda x: x['fcstValue'],
          'RN1': lambda x: x['fcstValue'],
          'T1H': lambda x: x['fcstValue'],
          'REH': lambda x: x['fcstValue'],
      }.get(category, lambda x: '')(item)

    csv_row = []
    for _, values in final_values.items():
      values['RN1'] = ({
          '강수없음': 0.0,
          '1mm 미만': 1.0,
          '30~50mm': 30.0,
          '50mm 이상': 50.0
      }.get(values['RN1'].strip(), lambda x: x))(values['RN1'])
      values['RN1'] = values['RN1'].replace('mm', '')
      csv_row.append(f"{base_date},{base_time},{values['PTY']},{values['RN1']},{values['T1H']},{values['REH']}")

    return '\n'.join(csv_row)

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
    start_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(days=1)
    save_file = 'forecast_' + start_time.strftime('%Y%m%d') + '.csv'
    current_time = start_time
    base_time = current_time.strftime('%H%M')

    # 파일 초기화
    with open(save_file, 'w') as f:
        f.write('# baseDate,baseTime,PTY,RN1,T1H,REH\n')

    while current_time <= end_time:
        # Prepare parameters
        params = {
            'serviceKey': SERVICE_KEY,
            'numOfRows': 100,
            'pageNo': 1,
            'dataType': 'JSON',
            'base_date': current_time.strftime('%Y%m%d'),
            'base_time': base_time,
            'nx': NX,
            'ny': NY
        }
        current_time += timedelta(hours=1)
        base_time = current_time.strftime('%H%M')
        print(f'Parameters: {params}')  # Log request parameters

        response = requests.get(BASE_URL, params=params)
        if response.status_code == 200:
            time.sleep(0.2)
            try:
                data = response.json()
                print(json.dumps(data, indent=2))
                csv_row_string = generate_csv_row(base_time, data)
                if not csv_row_string:
                    continue
            except:
                continue

            with open(save_file, 'a') as f:
              f.write(csv_row_string+'\n')
            continue

        print(f'#ERROR#: {response.status_code}')  # Handle errors
        break

if __name__ == '__main__':
    fetch_weather_data()
