#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# %%
# 파일 일기
with open('debug.html', 'r', encoding='utf-8') as f:
  html = f.read()
print(html)

# %%
from bs4 import BeautifulSoup
import re

txt = re.compile(r'출석.*주세요').findall(html)
print(txt)

# for line in soup.body:
#   if re.search(r'출석', line):
#     print(line)

# lines = soup.find_all(text="출석")
# print(lines)

# %%
import matplotlib.font_manager
fpaths = matplotlib.font_manager.findSystemFonts()

for path in fpaths:
  if path.__contains__('local'):
    f = matplotlib.font_manager.get_font(path)
    print(f.family_name)
