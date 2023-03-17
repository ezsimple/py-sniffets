#!/usr/bin/env python3
# -*- coding: utf8 -*-

#%%
import matplotlib.pyplot as plt
import numpy as np

## 한글화 작업
plt.rc('font', family = ['NanumGothic', 'FontAwesome'])
plt.rc('axes', unicode_minus = False)
plt.style.use('fivethirtyeight')
plt.rcParams['figure.facecolor'] = 'white'

def draw_donut(label, data):
  plt.pie(data, ## 파이차트 출력
    labels=label,
    autopct='%.1f%%', # 부채꼴 안에 표시될 숫자 형식(소수점 1자리까지 표시)
    startangle=90, # 축이 시작되는 각도 설정
    counterclock=True, # True: 시계방향순 , False:반시계방향순
    # explode=[0.05, 0.25, 0.05, 0.05], # 중심에서 벗어나는 정도 표시
    shadow=True, # 그림자 표시 여부
    colors = ['#ff9999', '#ffc000', '#8fd9b6', '#d395d0'], # colors=['gold','silver','whitesmoke','gray']
    wedgeprops = {'width':0.7,'edgecolor':'w','linewidth':3}
  )
  plt.show()


# %%
## 내부/외주 인력비율(MM)
label = ['내부', '외주', '예비']
data = [19,67.5,11] ## 빈도
draw_donut(label, data)

# %%
## 등급별(외주등급)-등급별 수
label = ['특급', '고급', '중급']
data = [1,11,3] ## 빈도
draw_donut(label, data)

# %%
## 예비 공수비율(MM)
label = ['예비', '투입']
data = [17, 89.5] ## 빈도
draw_donut(label, data)
