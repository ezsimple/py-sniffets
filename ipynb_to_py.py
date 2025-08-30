#!/usr/bin/env python3
import os
import subprocess

# 현재 디렉토리와 하위 디렉토리에서 모든 .ipynb 파일을 찾습니다.
# .ipynb -> .py 로 자동으로 변환해 줍니다.
for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith(".ipynb"):
            notebook_path = os.path.join(root, file)
            python_file = os.path.splitext(file)[0] + ".py"  # 파일 이름에서 확장자를 제거하고 .py로 변경
            output_path = os.path.join(root, python_file)

            # 변환할 파일의 디렉토리를 생성합니다.
            output_dir = os.path.dirname(output_path)
            os.makedirs(output_dir, exist_ok=True)

            # nbconvert를 사용하여 .ipynb 파일을 .py 파일로 변환합니다.
            subprocess.run(["jupyter", "nbconvert", "--to", "script", notebook_path, "--output", os.path.splitext(file)[0]], check=True)
            
            print(f"변환 완료: {notebook_path} -> {output_path}")

