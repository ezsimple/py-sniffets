# %%
import altair as alt
import pandas as pd
import numpy as np

# 예제 데이터 생성
np.random.seed(42)
dates = pd.date_range(start='2024-11-01', periods=30)
temperature = np.random.uniform(low=10, high=30, size=len(dates))
humidity = np.random.uniform(low=20, high=100, size=len(dates))
precipitation = np.random.poisson(lam=2, size=len(dates))

data = {
    '일자': dates,
    '온도(°C)': temperature,
    '습도(%)': humidity,
    '강수량(mm)': precipitation
}

df = pd.DataFrame(data)

# 온도 변화 시각화
temperature_chart = alt.Chart(df).mark_line(color='red').encode(
    x='일자:T',
    y=alt.Y('온도(°C):Q', axis=alt.Axis(title='온도(°C)')),
    tooltip=['일자:T', '온도(°C):Q']
)

# 습도 변화 시각화
humidity_chart = alt.Chart(df).mark_line(color='blue').encode(
    x='일자:T',
    y=alt.Y('습도(%):Q', axis=alt.Axis(title='습도(%)')),
    tooltip=['일자:T', '습도(%):Q']
)

# 강수량 변화 시각화
precipitation_chart = alt.Chart(df).mark_bar(color='green', opacity=0.5).encode(
    x='일자:T',
    y=alt.Y('강수량(mm):Q', axis=alt.Axis(title='강수량(mm)', orient='right')),
    tooltip=['일자:T', '강수량(mm):Q']
)

# 습도와 강수량 차트를 수직으로 결합
humidity_precipitation_layer = alt.layer(
    humidity_chart,
    precipitation_chart
).resolve_scale(
    y='independent'  # y축을 독립적으로 설정
).properties(
    width=600,
    height=200
)

# 최종 차트 결합
combined_layer = alt.vconcat(
    temperature_chart,
    humidity_precipitation_layer
).properties(
    title='온도, 습도, 강수량 변화'
)

# 차트 출력
combined_layer
