#!/usr/bin/env python3
# -*- coding: utf8 -*-

#%%
import matplotlib.pyplot as plt
import numpy as np

## 데이터 준비
frequency = [120,120,380,240,200] ## 빈도

plt.pie(
    frequency, ## 파이차트 출력
    autopct='%.1f%%', # 부채꼴 안에 표시될 숫자 형식(소수점 1자리까지 표시)
    startangle=90, # 축이 시작되는 각도 설정
    counterclock=True, # True: 시계방향순 , False:반시계방향순
    # explode=[0.05, 0.25, 0.05, 0.05], # 중심에서 벗어나는 정도 표시
    shadow=True, # 그림자 표시 여부
    colors = ['#ff9999', '#ffc000', '#8fd9b6', '#d395d0'], # colors=['gold','silver','whitesmoke','gray']
    wedgeprops = {'width':0.7,'edgecolor':'w','linewidth':3}
)

plt.show()
