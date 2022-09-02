#!/bin/bash
# 하위 파이썬 파일을 찾아서, 필요한 파이썬 패키지를 설치한다.
subdirs=$(find . -maxdepth 4 -type d -not -path '.')
for subdir in $subdirs
do
  pipreqs $subdir
  pip install -r $subdir/requirements.txt
  rm $subdir/requirements.txt
done
