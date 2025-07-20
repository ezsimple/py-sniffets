#!/usr/bin/env python3
import sys
import os
import shutil

'''
구글 드라이브와 iCloud가 상호 배타적이라 동시에 만족할 접점을 찾지 못함.
DropBox 의 경우 plugins 기준으로 vault 를 만들어서, 플러그인 삭제시 vault도 함께 삭제될 위험이 존재
그래서 복사할 파일을 구글 드라이브, iCloud에 동시에 보내는 기능을 구현.
iPad: iCloud(ReadOnly)
Android, MacBook: GoogleDrive 사용 (Read/Write)
'''

# Google Drive와 iCloud의 폴더 경로를 여기에 지정하세요
GOOGLE_DRIVE_PATH = os.path.expanduser('~/Google Drive/내 드라이브/DriveSyncFiles/메모장/obsidian') 
ICLOUD_PATH = os.path.expanduser('~/Library/Mobile Documents/iCloud~md~obsidian/Documents/obsidian_mac')

def main():
    if len(sys.argv) != 2:
        print("옵시디안 카피")
        print("사용법: python ocp.py <복사할_파일경로>")
        sys.exit(1)

    src_file = ''.join(sys.argv[1:])

    if not os.path.isfile(src_file):
        print(f"[오류] 파일이 존재하지 않습니다: {src_file}")
        sys.exit(1)

    # 파일명만 추출
    filename = os.path.basename(src_file)
    gd_dst = os.path.join(GOOGLE_DRIVE_PATH, filename)
    icloud_dst = os.path.join(ICLOUD_PATH, filename)

    # Google Drive로 복사
    try:
        os.makedirs(GOOGLE_DRIVE_PATH, exist_ok=True)
        shutil.copy2(src_file, gd_dst)
        print(f"Google Drive로 복사 완료: {gd_dst}")
    except Exception as e:
        print(f"[오류] Google Drive 복사 실패: {e}")

    # iCloud로 복사
    try:
        os.makedirs(ICLOUD_PATH, exist_ok=True)
        shutil.copy2(src_file, icloud_dst)
        print(f"iCloud로 복사 완료: {icloud_dst}")
    except Exception as e:
        print(f"[오류] iCloud 복사 실패: {e}")

if __name__ == "__main__":
    main() 
