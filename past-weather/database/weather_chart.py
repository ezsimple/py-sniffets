# %%
import plotly.graph_objects as go

# 데이터 예시
x_data = ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월']
temperature = [5, 7, 10, 15, 20, 25, 30, 29, 24, 18, 10, 5]  # 온도 데이터
humidity = [80, 75, 70, 65, 60, 55, 50, 55, 60, 70, 75, 80]  # 습도 데이터
precipitation = [30, 25, 20, 15, 10, 5, 0, 0, 5, 10, 20, 30]  # 강수량 데이터

# 차트 생성
fig = go.Figure()

# 온도 데이터 추가
fig.add_trace(go.Scatter(
    x=x_data,
    y=temperature,
    name='온도(°C)',
    yaxis='y1',
    mode='lines+markers',
    line=dict(color='red')
))

# 습도 데이터 추가
fig.add_trace(go.Scatter(
    x=x_data,
    y=humidity,
    name='습도(%)',
    yaxis='y2',
    mode='lines+markers',
    line=dict(color='blue')
))

# 강수량 데이터 추가
fig.add_trace(go.Bar(
    x=x_data,
    y=precipitation,
    name='강수(mm)',
    yaxis='y3',
    marker=dict(color='green')
))

# 레이아웃 설정
fig.update_layout(
    title='Weather Data',
    xaxis=dict(title='Month'),
    yaxis=dict(title='온도(°C)', side='left', position=0),
    yaxis2=dict(title='습도(%)', side='right', overlaying='y', position=1),
    yaxis3=dict(title='강수(mm)', side='right', overlaying='y', position=0.9),
    barmode='overlay'
)

# 차트 출력
fig.show()
