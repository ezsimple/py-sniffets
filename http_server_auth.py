#!/usr/bin/env python3 
'''
아이디, 암호 입력후 접근 가능함. 
암호는 (재)시작시마다 임의의 암호 생성 (ipass)
-d 경로에 .ignorefiles 내의 목록은 보이지 않음.
각 디렉토리의 .README 파일을 읽어서 출력
---
요구사항
---
1. "https://a1.mkeasy.kro.kr/dl/" 로 접근하면 로그인 필요
2. "https://a1.mkeasy.kro.kr/dl/" 다운로드 파일목록(디렉토리 포함) 표시
3. 다운로드 파일링크 클릭시 다운로드
4. 디렉토리클릭시 하위 디렉토리로 이동후 파알 다운로드 목록 표시
5. 다운로드 파일링크 클릭시 다운로드
6. 각 폴더별 .ignorefiles의 목록에 표시된 항목은 웹페이지에 미출력
- 각라인별 목록은 trim()
7. 각 폴더별 .README 파일이 존재할 경우 페이지 최상단에 표시
- # 으로 시작하는 라인은 미출력
- newline (\n)은 <br>로 처리
8. 예 GET : "https://a1.mkeasy.kro.kr/dl/파이썬/무지_이쁜_유니를_위한_초간단_파이썬_강의.pdf"
	/home/ubuntu/dl/파이썬/무지_이쁜_유니를_위한_초간단_파이썬_강의.pdf 파일 다운로드 시작
9. 서브디렉토리 목록의 경우, 상위폴더로 바로가기 .. 을 파일목록에 추가해줘.
'''
import re
import base64
import os
from functools import partial
from http.server import SimpleHTTPRequestHandler, test
import urllib.parse

class AuthHTTPRequestHandler(SimpleHTTPRequestHandler):
    """ Main class to present webpages and authentication. """

    WEB_SERVER_PREFIX='/dl/'

    def __init__(self, *args, **kwargs):
        username = kwargs.pop("username")
        password = kwargs.pop("password")
        self._auth = base64.b64encode(f"{username}:{password}".encode()).decode()
        super().__init__(*args, **kwargs)

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_AUTHHEAD(self):
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="Test"')
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_GET(self):
        """ Present frontpage with user authentication or serve files. """
        if self.headers.get("Authorization") is None:
            self.do_AUTHHEAD()
            self.wfile.write(b"no auth header received")
        elif self.headers.get("Authorization") == "Basic " + self._auth:
            # Check if the request is for a file or a directory
            path = self.translate_path(self.path)
            if os.path.isdir(path):
                self.handle_file_list()  # 파일 목록 처리
            elif os.path.isfile(path):
                self.handle_file_download(path)  # 파일 다운로드 처리
            else:
                self.send_error(404, "File not found")
        else:
            self.do_AUTHHEAD()
            self.wfile.write(b"not authenticated")

    def handle_file_list(self):
        """ List files in the directory, filtering out ignored files. """
        path = self.translate_path(self.path)
        if os.path.isdir(path):
            files = os.listdir(path)

            # .ignorefiles에서 패턴 읽기
            ignore_file_path = os.path.join(path, '.ignorefiles')
            ignored_patterns = []
            if os.path.isfile(ignore_file_path):
                with open(ignore_file_path, 'r') as f:
                    ignored_patterns = [line.strip() for line in f if line.strip()]

            # 정규 표현식 패턴으로 변환
            regex_patterns = [re.escape(pattern).replace(r'\*', '.*') for pattern in ignored_patterns]

            # 필터링된 파일 목록 생성
            filtered_files = [file for file in files if not any(re.match(pattern, file) for pattern in regex_patterns)]

            # README 파일 내용 표시
            readme_content = self.get_readme_content(path)
            
            # HTML 응답 생성
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")  # UTF-8 인코딩 설정
            self.end_headers()
            self.wfile.write(b'''
                <!DOCTYPE html>
                <html lang="ko">
                <body>
            ''')

            if readme_content:
                self.wfile.write(f'<div>{readme_content}</div>'.encode('utf-8'))

            self.wfile.write(b'''
                <h2>File List</h2>
                <ul>
            ''')

            # 상위 폴더로 가는 링크 추가
            parent_directory = os.path.dirname(self.path)
            self.wfile.write(f'<li><a href="{self.WEB_SERVER_PREFIX.rstrip("/")}{parent_directory}">..</a></li>'.encode('utf-8'))

            for file in filtered_files:
                # 링크 수정: 서브 디렉토리 경로를 포함하도록 변경
                file_path = os.path.join(self.path, file)
                file_link = f'{self.WEB_SERVER_PREFIX.rstrip("/")}{file_path}'  # 마지막 / 제거
                if os.path.isdir(os.path.join(path, file)): # 주의: path만 사용함.
                  self.wfile.write(f'<li><a href="{file_link}">{file}/</a></li>'.encode('utf-8'))  # 디렉토리인 경우
                else:
                  self.wfile.write(f'<li><a href="{file_link}">{file}</a></li>'.encode('utf-8'))  # 파일인 경우


            self.wfile.write(b'''
                </ul>
                </body>
                </html>
            ''')
        else:
            self.send_error(404, "Directory not found")

    def handle_file_download(self, path):
      """ Serve the file for download. """
      self.send_response(200)
      self.send_header("Content-type", "application/octet-stream")  # 다운로드용 MIME 타입

      # 파일 이름을 URI 인코딩하여 Content-Disposition 헤더에 추가
      filename = os.path.basename(path)
      encoded_filename = urllib.parse.quote(filename)  # URI 인코딩
      self.send_header("Content-Disposition", f'attachment; filename="{encoded_filename}"; filename*=UTF-8\'{encoded_filename}')

      self.end_headers()

      # 절대 경로 출력
      print(f"Downloading file from: {os.path.abspath(path)}")

      with open(path, 'rb') as f:
        self.wfile.write(f.read())

    def get_readme_content(self, path):
        """ Read README file content and format it. """
        readme_path = os.path.join(path, '.README')
        if os.path.isfile(readme_path):
            with open(readme_path, 'r') as f:
                content = f.readlines()
            # #으로 시작하는 라인 제외하고, 줄바꿈 처리
            formatted_content = '<br>'.join(line.strip() for line in content if not line.startswith('#'))
            return formatted_content
        return ""

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--cgi", action="store_true", help="Run as CGI Server")
    parser.add_argument(
        "--bind",
        "-b",
        metavar="ADDRESS",
        default="127.0.0.1",
        help="Specify alternate bind address [default: all interfaces]",
    )
    parser.add_argument(
        "--directory",
        "-d",
        default=os.getcwd(),
        help="Specify alternative directory [default: current directory]",
    )
    parser.add_argument(
        "port",
        action="store",
        default=8000,
        type=int,
        nargs="?",
        help="Specify alternate port [default: 8000]",
    )
    parser.add_argument("--username", "-u", metavar="USERNAME")
    parser.add_argument("--password", "-p", metavar="PASSWORD")
    args = parser.parse_args()
    handler_class = partial(
        AuthHTTPRequestHandler,
        username=args.username,
        password=args.password,
        directory=args.directory,
    )
    test(HandlerClass=handler_class, port=args.port, bind=args.bind)

