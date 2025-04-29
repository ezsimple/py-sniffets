import os
import re
import requests
import json
import time
from html.parser import HTMLParser
from urllib.parse import urlparse
from typing import List, Dict, Optional, Tuple
import timeit
import functools
from datetime import timedelta
from datetime import datetime

class BookmarkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.bookmarks = []
        self.current_folder = None
        self.folder_stack = []
        self.current_bookmark = None
        self.capture_title = False
        self.in_bookmark = False
        self.folder_structure = {"name": "Root", "children": [], "folders": {}}
        self.current_path = [self.folder_structure]

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        # 북마크 폴더 시작
        if tag == 'h3':
            folder_name = attrs_dict.get('personal_toolbar_folder', None)
            if folder_name is None:
                folder_name = ""  # 실제 이름은 데이터에서 채워질 것임

            new_folder = {"name": folder_name, "children": [], "folders": {}}
            self.current_folder = new_folder
            self.folder_stack.append(new_folder)

            # Add Date Added attribute if available
            if 'add_date' in attrs_dict:
                new_folder['add_date'] = attrs_dict['add_date']

            self.capture_title = True

        # 북마크 폴더 그룹 시작
        elif tag == 'dl':
            if self.current_folder:
                current = self.current_path[-1]
                if self.current_folder["name"]:
                    current["folders"][self.current_folder["name"]] = self.current_folder
                    self.current_path.append(self.current_folder)

        # 북마크 항목
        elif tag == 'a' and 'href' in attrs_dict:
            self.in_bookmark = True
            self.current_bookmark = {
                'url': attrs_dict['href'],
                'add_date': attrs_dict.get('add_date', ''),
                'icon': attrs_dict.get('icon', ''),
                'title': '',  # 내용에서 채워질 것임
                'is_valid': True  # 기본값은 유효함
            }
            self.capture_title = True

    def handle_endtag(self, tag):
        # 북마크 폴더 종료
        if tag == 'dl' and self.folder_stack:
            if len(self.current_path) > 1:
                self.current_path.pop()

        # 북마크 항목 종료
        elif tag == 'a' and self.in_bookmark:
            if self.current_bookmark:
                current_folder = self.current_path[-1]
                current_folder["children"].append(self.current_bookmark)
                self.bookmarks.append(self.current_bookmark)
                self.current_bookmark = None
                self.in_bookmark = False
                self.capture_title = False

    def handle_data(self, data):
        # 현재 폴더 제목 설정
        if self.capture_title and self.current_folder is not None and not self.in_bookmark:
            self.current_folder["name"] = data.strip()
            self.capture_title = False

        # 북마크 제목 설정
        elif self.capture_title and self.in_bookmark and self.current_bookmark is not None:
            self.current_bookmark["title"] = data.strip()
            self.capture_title = False

    def get_all_bookmarks(self) -> List[Dict]:
        """모든 북마크 항목 반환"""
        return self.bookmarks

    def get_folder_structure(self) -> Dict:
        """폴더 구조 반환"""
        return self.folder_structure

    def print_folder_structure(self, folder=None, level=0):
        """폴더 구조를 트리 형태로 출력"""
        if folder is None:
            folder = self.folder_structure

        indent = "  " * level
        print(f"{indent}📁 {folder['name']}")

        # 북마크 항목 출력
        for bookmark in folder["children"]:
            status = "✅" if bookmark.get('is_valid', True) else "❌"
            print(f"{indent}  {status} {bookmark['title']} - {bookmark['url']}")

        # 하위 폴더 출력
        for subfolder_name, subfolder in folder["folders"].items():
            self.print_folder_structure(subfolder, level + 1)

def parse_bookmarks_file(file_path: str) -> Tuple[List[Dict], Dict]:
    """북마크 HTML 파일을 파싱하여 북마크 목록과 폴더 구조 반환"""
    parser = BookmarkParser()

    with open(file_path, 'r', encoding='utf-8') as file:
        bookmark_html = file.read()

    parser.feed(bookmark_html)

    return parser.get_all_bookmarks(), parser.get_folder_structure()

def is_valid_url(url: str) -> bool:
    """URL 형식이 유효한지 검사"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def is_success_status_code(status_code: int) -> bool:
    """HTTP 상태 코드가 성공(2xx)인지 확인"""
    return 200 <= status_code < 400

def check_url_status(url: str, timeout=3) -> bool:
    """URL에 HTTP 요청을 보내 상태 확인"""
    if not is_valid_url(url):
        return False
        
    try:
        # HEAD 요청으로 효율적으로 상태 확인
        response = requests.head(url, allow_redirects=True, timeout=timeout)
        return is_success_status_code(response.status_code)
    except requests.RequestException:
        try:
            # HEAD 요청이 실패하면 GET 요청 시도
            response = requests.get(url, timeout=timeout, stream=True)
            response.close()  # 응답 본문을 다운로드하지 않도록 연결 종료
            return is_success_status_code(response.status_code)
        except requests.RequestException:
            return False

def verify_bookmarks(bookmarks: List[Dict], check_online=True, max_bookmarks=None) -> Tuple[List[Dict], List[Dict]]:
    """북마크 목록에서 유효한 북마크와 깨진 북마크 필터링"""
    valid_bookmarks = []
    broken_bookmarks = []
    
    # 검증할 북마크 수 제한 (선택 사항)
    if max_bookmarks:
        bookmarks_to_check = bookmarks[:max_bookmarks]
    else:
        bookmarks_to_check = bookmarks
    
    total = len(bookmarks_to_check)
    
    print(f"\n북마크 유효성 검사 시작 ({total}개)...")
    
    for i, bookmark in enumerate(bookmarks_to_check):
        url = bookmark['url']
        
        # URL 형식 검증
        if not is_valid_url(url):
            bookmark['is_valid'] = False
            broken_bookmarks.append(bookmark)
            print(f"[{i+1}/{total}] ❌ 잘못된 URL 형식: {bookmark['title']} - {url}")
            continue
        
        # 온라인 연결 검증 (선택적)
        if check_online:
            print(f"[{i+1}/{total}] 검사 중: {bookmark['title']}")
            is_valid = check_url_status(url)
            bookmark['is_valid'] = is_valid
            
            if is_valid:
                valid_bookmarks.append(bookmark)
                print(f"[{i+1}/{total}] ✅ 유효함: {bookmark['title']}")
            else:
                broken_bookmarks.append(bookmark)
                print(f"[{i+1}/{total}] ❌ 깨진 링크: {bookmark['title']} - {url}")
            
            # 서버 부하 방지를 위한 약간의 지연
            time.sleep(0.1)
        else:
            # 온라인 검사를 건너뛰면 모두 유효하다고 가정
            bookmark['is_valid'] = True
            valid_bookmarks.append(bookmark)
    
    return valid_bookmarks, broken_bookmarks

def extract_domain(url: str) -> str:
    """URL에서 도메인 이름 추출"""
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    # www. 제거
    if domain.startswith('www.'):
        domain = domain[4:]
    return domain

def update_folder_structure_validity(folder_structure: Dict) -> None:
    """폴더 구조 내의 모든 북마크에 유효성 표시 업데이트"""
    # 현재 폴더의 북마크 업데이트
    for bookmark in folder_structure["children"]:
        if 'is_valid' not in bookmark:
            bookmark['is_valid'] = True
    
    # 모든 하위 폴더 재귀 처리
    for subfolder_name, subfolder in folder_structure["folders"].items():
        update_folder_structure_validity(subfolder)

# 유효한 북마크 목록을 HTML 파일로 저장
def save_valid_bookmarks_html(valid_bookmarks: List[Dict], output_path: str):
    """유효한 북마크 목록을 HTML 파일로 저장"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('<!DOCTYPE html>\n<html lang="ko">\n<head>\n')
        f.write('<meta charset="UTF-8">\n<title>유효한 북마크 목록</title>\n')
        f.write('</head>\n<body>\n')
        f.write(f'<h1>유효한 북마크 목록 ({len(valid_bookmarks)}개)</h1>\n')
        f.write('<ul>\n')
        for bookmark in valid_bookmarks:
            title = bookmark.get('title', bookmark.get('url', ''))
            url = bookmark.get('url', '')
            f.write(f'<li><a href="{url}" target="_blank">{title}</a></li>\n')
        f.write('</ul>\n')
        f.write('</body>\n</html>\n')

# 깨진 링크 목록을 파일로 저장
def save_broken_links_report(broken_bookmarks: List[Dict], output_path: str) -> None:
    """깨진 링크 목록을 파일로 저장"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# 깨진 북마크 목록\n\n")
        for i, bookmark in enumerate(broken_bookmarks):
            f.write(f"{i+1}. [{bookmark['title']}]({bookmark['url']})\n")
            f.write(f"   - 추가 날짜: {bookmark.get('add_date', '알 수 없음')}\n")
            f.write("\n")

def format_execution_time(execution_time):
    """
    실행 시간(초)을 받아 일, 시간, 분, 초, 밀리초 형식의 문자열로 반환하는 함수

    Args:
        execution_time (float): 측정된 실행 시간 (초 단위)

    Returns:
        str: 형식화된 실행 시간 문자열
    """
    # 시간을 timedelta 객체로 변환
    time_delta = timedelta(seconds=execution_time)

    # 일, 시, 분, 초 형식으로 변환
    days = time_delta.days
    hours, remainder = divmod(time_delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = time_delta.microseconds // 1000

    # 출력 형식 설정
    if days > 0:
        return f"{days}일 {hours}시간 {minutes}분 {seconds}초 {milliseconds}밀리초"
    elif hours > 0:
        return f"{hours}시간 {minutes}분 {seconds}초 {milliseconds}밀리초"
    elif minutes > 0:
        return f"{minutes}분 {seconds}초 {milliseconds}밀리초"
    else:
        return f"{seconds}초 {milliseconds}밀리초"

def timer_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        formatted_time = format_execution_time(execution_time)
        print(f"함수 실행 시간: {formatted_time}")
        return result
    return wrapper

@timer_decorator
def main(bookmarks_file_path: str, check_online=False, max_bookmarks=None):
    """메인 함수: 북마크 파일 경로를 파라미터로 받음"""
    if os.path.exists(bookmarks_file_path):
        bookmarks, folder_structure = parse_bookmarks_file(bookmarks_file_path)
        
        print(f"총 {len(bookmarks)}개의 북마크를 발견했습니다.")
        
        # 북마크 유효성 검사 (check_online=True면 실제 HTTP 요청 수행)
        valid_bookmarks, broken_bookmarks = verify_bookmarks(
            bookmarks, 
            check_online=check_online,
            max_bookmarks=max_bookmarks
        )
        
        # 폴더 구조의 북마크 유효성 정보 업데이트
        update_folder_structure_validity(folder_structure)
        
        # 결과 출력
        print("\n폴더 구조:")
        parser = BookmarkParser()
        parser.folder_structure = folder_structure
        parser.print_folder_structure()
        
        # 첫 5개 북마크 출력
        print("\n북마크 샘플 (처음 5개):")
        for i, bookmark in enumerate(bookmarks[:5]):
            status = "✅" if bookmark.get('is_valid', True) else "❌"
            print(f"{i+1}. {status} {bookmark['title']} - {bookmark['url']}")
        
        print(f"\n전체 {len(bookmarks)}개 북마크")
        print(f"✅ 유효한 북마크: {len(valid_bookmarks)}개")
        print(f"❌ 깨진 북마크: {len(broken_bookmarks)}개")
        
        # 깨진 링크 보고서 저장
        if broken_bookmarks:
            report_path = "broken_bookmarks_report.md"
            save_broken_links_report(broken_bookmarks, report_path)
            print(f"\n깨진 북마크 목록이 '{report_path}'에 저장되었습니다.")

        # 유효한 북마크 HTML 저장
        html_output_path = "valid_bookmarks.html"
        save_valid_bookmarks_html(valid_bookmarks, html_output_path)
        print(f"\n유효한 북마크 목록이 '{html_output_path}'에 저장되었습니다.")
        
        return bookmarks, folder_structure, valid_bookmarks, broken_bookmarks
    else:
        print(f"파일을 찾을 수 없습니다: {bookmarks_file_path}")
        return [], {}, [], []



# 명령줄에서 실행될 때
if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='크롬 북마크 HTML 파일을 파싱하고 깨진 링크 검사')
    parser.add_argument('file', nargs='?', default="bookmarks.html", help='북마크 HTML 파일 경로')
    parser.add_argument('--check-online', action='store_true', help='온라인 상태 검사 수행 (시간 소요)')
    parser.add_argument('--max', type=int, help='검사할 최대 북마크 수')
    
    args = parser.parse_args()
    main(args.file, check_online=args.check_online, max_bookmarks=args.max)
