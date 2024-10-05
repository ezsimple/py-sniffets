#!/usr/bin/env python3
'''
로그인, 파일 탐색 및 다운로드 기능: 사용자 인증 후 서버의 파일 시스템을 탐색하고 파일을 다운로드할 수 있는 기능을 제공합니다.
.ignorefiles의 내용은 서버파일목록에 표시하지 않습니다.
'''
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import urllib.parse
import re

# 사용자 인증 정보
USERNAME = "yoon"
PASSWORD = "dbsl2Qh!"

# 서버정보
PORT = 3333

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 로그인 페이지 요청 처리
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'''
                <html>
                <body>
                    <h2>Login</h2>
                    <form method="POST" action="/login">
                        <label for="username">Username:</label><br>
                        <input type="text" id="username" name="username"><br>
                        <label for="password">Password:</label><br>
                        <input type="password" id="password" name="password"><br><br>
                        <input type="submit" value="Login">
                    </form>
                </body>
                </html>
            ''')
        elif self.path.startswith('/files'):
            # 파일 및 디렉토리 목록 요청 처리
            self.handle_file_list()
        elif self.path.startswith('/download'):
            # 파일 다운로드 요청 처리
            self.handle_file_download()
        else:
            self.send_error(404)

    def do_POST(self):
        # 로그인 처리
        if self.path == '/login':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode()
            params = urllib.parse.parse_qs(post_data)

            username = params.get('username', [None])[0]
            password = params.get('password', [None])[0]

            if username == USERNAME and password == PASSWORD:
                self.send_response(302)  # Redirect
                self.send_header('Location', '/files')
                self.end_headers()
            else:
                self.send_response(401)  # Unauthorized
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'Invalid credentials. Please <a href="/">try again</a>.')

    def handle_file_list(self):
        # 현재 디렉토리의 파일 및 디렉토리 목록을 표시
        path = self.path[6:] if self.path != '/files' else '.'
        files = os.listdir(path)

        # .ignorefiles에 있는 패턴을 제외
        ignore_file_path = os.path.join(path, '.ignorefiles')
        ignored_patterns = []
        if os.path.isfile(ignore_file_path):
          with open(ignore_file_path, 'r') as f:
            ignored_patterns = f.read().splitlines()

        # 정규 표현식 패턴으로 변환
        regex_patterns = [re.escape(pattern).replace(r'\*', '.*') for pattern in ignored_patterns]

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'''
            <html>
            <body>
                <h2>File List</h2>
                <ul>
        ''')
        for file in files:
            if any(re.match(pattern, file) for pattern in regex_patterns):
                continue  # 패턴에 맞는 파일은 건너뜀
            file_path = os.path.join(path, file)
            if os.path.isdir(file_path):
                self.wfile.write(f'<li><a href="/files/{file}">{file}/</a></li>'.encode())
            else:
                self.wfile.write(f'<li><a href="/download?file={file}">{file}</a></li>'.encode())
        self.wfile.write(b'''
                </ul>
            </body>
            </html>
        ''')

    def handle_file_download(self):
        # 파일 다운로드 처리
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        file_name = params.get('file', [None])[0]
        
        if file_name:
            file_path = os.path.join('.', file_name)
            if os.path.isfile(file_path):
                self.send_response(200)
                self.send_header('Content-Disposition', f'attachment; filename="{file_name}"')
                self.send_header('Content-type', 'application/octet-stream')
                self.end_headers()

                with open(file_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, "File not found")
        else:
            self.send_error(400, "Bad request")

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=PORT):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting http server on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
