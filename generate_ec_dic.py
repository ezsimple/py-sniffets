#!/usr/bin/env python3

# %%
from urllib.parse import quote, unquote
import requests as r
import json
import os

def http_get(url):
  response = r.get(url)
  encoding = response.encoding
  result = response.text.encode(encoding, "utf-8")
  result = result.decode()
  return result

# %%
# 한국 은행 경제 용어 사전 데이터 모으기
import pandas as pd
ko_category = 'ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅊㅋㅌㅍㅎ'
en_category = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

ec_word_nm_list = [] # 경제용어
ec_word_sn_list = [] # 경제용어번호
comment_list = [] # 설명
relate_list = [] # 연관항목
for c in ko_category:
  url = 'https://www.bok.or.kr/portal/search/dicSearch.do?collection=dic&category='+c
  result = http_get(url)
  parsed = json.loads(result)

  for item in parsed:
    ecWordSn = item['EC_WORD_SN']
    url = 'https://www.bok.or.kr/portal/ecEdu/ecWordDicary/searchCont.json?ecWordSn='+ecWordSn
    result = http_get(url)
    out = json.loads(result)

    ec_word_nm_list.append(out['result']['ecWordNm'])
    ec_word_sn_list.append(out['result']['ecWordSn'])
    comment_list.append(out['result']['ecWordCn'])
    relate_list.append(out['relateList'])

df = pd.DataFrame({'ecWordSn': ec_word_sn_list, 'ecWordNm': ec_word_nm_list, 'ecWordCn': comment_list, 'relateList': relate_list})

# %%
file_name = '한국은행_경제용어_사전.csv'
df.to_csv(file_name, index=False)

# %%
# 한국 은행 경제 용어 사전 CSV 파일 저장
dict_df = pd.read_csv(file_name, index_col='ecWordSn')
dict_df.head()

# %%
dict_df.shape

# %%
# static 링크 정정
import pandas as pd
import re
import html

def cleanhtml(raw_html):
  cleanr = re.compile('<.*?>|&.{4};')
  cleantext = re.sub(cleanr, '', str(raw_html))
  clean = re.sub('\s+',' ',cleantext)
  return html.unescape(clean) # replaces the special characters

def fix_static_path(row):
  return str(row).replace('"/static', '"https://www.bok.or.kr/static')

dict_df.columns

# %%
dict_df.iloc[2]['ecWordCn']

# %%
dict_df['ecWordCn'] = dict_df['ecWordCn'].apply(lambda x : fix_static_path(x))
dict_df.to_csv(file_name, index=False)

# %%
dict_df.tail()