# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# 예제 데이터 생성
np.random.seed(42)  # 재현성을 위해 시드 설정
dates = pd.date_range(start='2024-11-01', periods=30)
temperature = np.random.uniform(low=10, high=30, size=len(dates))  # 10°C에서 30°C 사이의 온도
humidity = np.random.uniform(low=20, high=100, size=len(dates))  # 20%에서 100% 사이의 습도
precipitation = np.random.poisson(lam=2, size=len(dates))  # 평균 2mm의 강수량

data = {
    '일자': dates,
    '온도(°C)': temperature,
    '습도(%)': humidity,
    '강수량(mm)': precipitation
}

df = pd.DataFrame(data)

# 3D 산점도 생성
fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection='3d')

# 산점도 그리기
sc = ax.scatter(df['온도(°C)'], df['습도(%)'], df['강수량(mm)'], c=df['강수량(mm)'], cmap='viridis', s=100)

# 축 레이블 설정
ax.set_xlabel('온도 (°C)')
ax.set_ylabel('습도 (%)')
ax.set_zlabel('강수량 (mm)')
ax.set_title('3D 기상 데이터 시각화')

# 색상 바 추가
cbar = plt.colorbar(sc)
cbar.set_label('강수량 (mm)')

# 그래프 보여주기
plt.show()
