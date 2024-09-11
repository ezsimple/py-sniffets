#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# %%
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rc
from enum import Enum
import matplotlib.colors as mcolors
import matplotlib.font_manager as fm

# ubuntu에 한글 폰트 적용하기
# https://velog.io/@euisuk-chung/파이썬-우분투에서-한글-폰트-설치하고-matplotlib에-사용하기
print(mpl.__file__)
print([f.fname for f in fm.fontManager.ttflist])

# %%

fp=r'/usr/share/fonts/truetype/d2coding/D2Coding/D2Coding-Ver1.3.2-20180524.ttf'
fs = 14
fn = 'D2Coding'
fe = fm.FontEntry(
    fname=fp,
    name=fn
)
fm.fontManager.ttflist.insert(0, fe)
plt.rcParams.update({'font.size': fs, 'font.family': fn})

# %%

print([f.name for f in fm.fontManager.ttflist])

# %%

for nm in fm.get_font_names():
    if "Na" in nm:
        print(nm)

print("mpl cachedir : {}".format(mpl.get_cachedir()))
# WSL2에서 plt.show()가 안되는 문제 보완
# import matplotlib
# matplotlib.use('TkAgg')

# %%
# 한글 깨짐 방지
rc('font', family='AppleGothic')  # 폰트 설정
plt.rcParams['axes.unicode_minus'] = False  # 유니코드 마이너스 설정

# 무지개 색상을 순서대로 생성
def sched_colors():
    base_colors = list(mcolors.XKCD_COLORS.values())
    colors = []
    for color in base_colors:
        mcolor = mcolors.to_rgba(color, alpha=0.4)  # Adjust alpha for pastel effect
        colors.append(mcolor)
    return colors


# 계획표 색상 배열 가져오기
sched_colors = sched_colors()

# 색상을 enum으로 선언 (가독성)
class Color(Enum):
    SLEEP = sched_colors[0]   # 수면
    MEAL = sched_colors[1]    # 식사
    BUSINESS = sched_colors[2]# 업무
    COMMUTE = sched_colors[3] # 출퇴근
    REST = sched_colors[6]    # 휴식
    EXERCISE = sched_colors[5]# 운동

# 각 활동에 소비되는 시간을 입력 (총 24시간 기준 입니다)
# 활동배열의 처음과 끝은 수면 이어야 합니다.
activities = ['수면', '운동', '식사', '출근', '오전업무', '식사', '오후업무', '퇴근', '식사', '휴식', '']
hours = [5, 1, 1, 1, 4, 1, 5, 1, 1, 2, 2]

# 색깔 지정
colors = (Color.SLEEP.value, Color.EXERCISE.value, Color.MEAL.value, Color.COMMUTE.value, Color.BUSINESS.value, 
          Color.MEAL.value, Color.BUSINESS.value, Color.COMMUTE.value, Color.MEAL.value, 
          Color.REST.value, Color.SLEEP.value)

# 시간 값을 출력하는 autopct 함수 정의
def time_autopct(pct):
    total_hours = sum(hours)
    hours_value = int(round(pct * total_hours / 100.0))  # 퍼센트를 시간으로 변환
    # return f'{hours_value}시간'

# 원형 그래프 그리기
plt.figure(figsize=(8, 8))
wedges, texts, autotexts = plt.pie(hours, labels=None, autopct=time_autopct, startangle=90, colors=colors, counterclock=False)

# 원 둘레에 시간(0~24시) 표시
ax = plt.gca()  # 현재 축 가져오기
ax.set_aspect('equal')  # 원을 유지하기 위해 비율 설정

# 원 둘레에 시간 표시 (0시 ~ 23시) - 시계 방향
for hour in range(24):
    angle = 360 * (hour / 24)  # 시계 방향으로 시간에 해당하는 각도 계산
    x = np.cos(np.radians(90 - angle))  # x 좌표 (90도 이동으로 시계 방향 맞추기)
    y = np.sin(np.radians(90 - angle))  # y 좌표
    plt.text(x * 1.1, y * 1.1, f'{hour}시', ha='center', va='center')  # 원 밖에 시간 표시

# 각 활동명을 원 안에 표시
for i, (wedge, activity) in enumerate(zip(wedges, activities)):
    angle = (wedge.theta2 + wedge.theta1) / 2  # 각 활동의 중앙 각도 계산
    x = np.cos(np.radians(angle)) * 0.6  # x 좌표 (원의 60% 지점에 활동명을 표시)
    y = np.sin(np.radians(angle)) * 0.6  # y 좌표
    plt.text(x, y, activity, ha='center', va='center')  # 원 안에 활동명 표시

# 그래프 제목 추가
plt.title('일일 시간 계획표')

# 그래프 보여주기
plt.show()
