#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# %%

import pandas as pd
import pygwalker as pyg

# 활동 데이터 정의
data = {
    '활동': ['수면', '운동', '식사', '출근', '오전업무', '식사', '오후업무', '퇴근', '식사', '휴식', '수면'],
    '시간(시간)': [5, 1, 1, 1, 4, 1, 5, 1, 1, 2, 2],
}

# pandas 데이터프레임으로 변환
df = pd.DataFrame(data)

# PyGWalker로 시각화
pyg.walk(df)
