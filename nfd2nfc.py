#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 맥에서 한글 파일명 자소분리 문제 해결
# 이미 자소분리되어 있는 파일명을 NFC형식으로 변환해 주는 유틸리티
# - 한글 자소 분리 문제
# - Mac은 한글 문자의 정규화 방식으로 NFD(Normalization Form Decomposition)를 사용하는데, 
#   Windows나 대부분의 Linux distribution에서는 NFC(Normalization Form Decomposition)를 사용하기 때문
# 
# https://devocean.sk.com/blog/techBoardDetail.do?ID=164376

import argparse
import os
import unicodedata

####################################################################
## 파일명을 NFC(완성형) 를 NFD(조합형) 로 변경
####################################################################
def normalize_filename(file_path):
    # 파일명에서 디렉터리 경로와 파일명을 분리
    directory, filename = os.path.split(file_path)

    # NFC로 정규화한 파일명 생성
    normalized_filename = unicodedata.normalize('NFC', filename)

    # 디렉터리와 정규화된 파일명을 합쳐서 새로운 파일 경로 생성
    normalized_file_path = os.path.join(directory, normalized_filename)

    # 파일명 변경
    os.rename(file_path, normalized_file_path)
    print(f"[+] {file_path} -> {normalized_file_path}")


####################################################################
## 변경 대상 파일명 찾아서 normalize_filename() 호출
####################################################################
def normalize_filenames_in_directory(directory, recursive=False, target_extension=None):
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)

            # 특정 확장자에 해당하는 파일만 변경
            if target_extension is None or file_path.lower().endswith(target_extension.lower()):
                normalize_filename(file_path)

        # 만약 recursive 옵션이 활성화되었으면, 하위 디렉터리의 탐색을 계속
        if not recursive:
            break


####################################################################
## 인자 설정 및 변경 코드 호출
####################################################################
def main():
    parser = argparse.ArgumentParser(
        description='Normalize Korean filenames in a directory.',
        usage='%(prog)s [directory] [-r|--recursive] [-e|--extension <extension>]'
    )
    parser.add_argument('directory', metavar='directory', type=str, nargs='?', default=os.getcwd(),
                        help='The target directory (default: current directory)')
    parser.add_argument('-r', '--recursive', action='store_true', help='Enable recursive search')
    parser.add_argument('-e', '--extension', type=str, default=None,
                        help='Target file extension to change (default: None)')

    args = parser.parse_args()

    target_directory = args.directory
    recursive = args.recursive
    target_extension = args.extension

    # 디렉터리 내의 특정 확장자를 가진 파일들의 이름을 NFC로 정규화
    normalize_filenames_in_directory(target_directory, recursive, target_extension)

if __name__ == '__main__':
    main()

