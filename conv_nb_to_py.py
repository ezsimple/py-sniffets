#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# %%
# jupyter nbconvert --to script xxx.ipynb

# %%
import os
import subprocess

# 서브 디렉토리 파일명 가져오기
def get_file_names_with_rel_path(dir_path):
  subdir_file_name = []
  for root, dirs, files in os.walk(dir_path):
      for file in files:
        if file.endswith(".ipynb"):
          subdir_file_name.append(os.path.join(root, file))
  return subdir_file_name

# subshell 실행하기
def do(app):
    print(app)
    subprocess.call(app, shell=True)

# %%
# .ipynb 파일 목록 가져오기
files = get_file_names_with_rel_path('./')
print(files)

# %%
# .ipynb to .py 파일 변환하기
for file in files:
  cmd = 'jupyter nbconvert --to script ' + '\'' + file + '\''
  do(cmd)

  file = file.replace('.ipynb', '.py')
  cmd = 'sed -i -e "s/^# In.*$/# %%/" ' + '\'' + file + '\''
  do(cmd)

