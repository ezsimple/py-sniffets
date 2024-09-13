# %%
import plotly.graph_objects as go
import numpy as np

# 각 활동에 소비되는 시간을 입력 (총 24시간 기준)
activities = ['수면', '운동', '식사', '출근', '오전업무', '식사', '오후업무', '퇴근', '식사', '휴식', '']
hours = [5, 1, 1, 1, 4, 1, 5, 1, 1, 2, 2]

# 색상 배열
colors = ['#FF9999', '#66B3FF', '#99FF99', '#FFCC99', '#FFD700', '#FF7F50', '#87CEFA', '#DDA0DD', '#FF69B4', '#BA55D3', '#FF6347']

# 원형 그래프 만들기
fig = go.Figure()

# 파이 차트 생성
fig.add_trace(go.Pie(
    labels=activities, 
    values=hours, 
    marker=dict(colors=colors), 
    hoverinfo='label+percent+value', 
    textinfo='label+value', 
    hole=0.3
))

# 원 둘레에 시간(0시 ~ 23시) 표시
for hour in range(24):
    angle = 360 * (hour / 24)  # 시계 방향으로 시간에 해당하는 각도 계산
    x = np.cos(np.radians(90 - angle)) * 0.95 + 0.5  # x 좌표 (좌표계를 0~1 사이로 맞추기)
    y = np.sin(np.radians(90 - angle)) * 0.95 + 0.5  # y 좌표
    fig.add_annotation(
        x=x, y=y, 
        text=f'{hour}시', 
        showarrow=False, 
        font=dict(size=12),
        xanchor='center', 
        yanchor='middle',
        xref="paper",  # paper 좌표계 사용
        yref="paper"
    )

# 제목 추가
fig.update_layout(
    title_text='일일 시간 계획표',
    annotations=[dict(text='활동', x=0.5, y=0.5, font_size=20, showarrow=False)],
    showlegend=False
)

# 그래프 보여주기
fig.show()
