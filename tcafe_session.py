#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ==================================
# tcafe 자동 출석 체크하는 프로그램
# ==================================
# 좋은 소스가 있네요. 공부합시다.
# https://github.com/lumyjuwon/NaverCaptcha
# ==================================
# %%

import configparser
import contextlib
import io
import os
import platform
import re
import subprocess

from LogUtil import LogUtil

from lxml import html
import requests as r
from fake_useragent import UserAgent
import errno
from bs4 import BeautifulSoup
import telegram

# from win32process import CREATE_NO_WINDOW

class AutoTcafe:

    def __init__(self):
        self.config = configparser.RawConfigParser()
        self.configFile = 'tcafe_config.ini'
        self.readConfig()
        self.logging = LogUtil('TCAFE_ACCESS')
        # chrome debugger 의 Network 에서 headers 값을 가져와 셋팅한다.
        # 브라우저에서 최초 접근시에는 브라우저 Request의 헤더값 밖에는 없다.
        #
        # 현재는 일반 브라우저로 접속할 경우
        # tCafe는 쿠키값을 가지고서 reCaptcha 를 감지하고 있다. (쿠키 삭제시 403 에러 발생)
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Cookie': '__cfduid=df668e1d883ce6e3bb2ecdd7536cb4b731558682605; f33d2ed86bd82d4c22123c9da444d8ab=MTU1ODY4MjYxNQ%3D%3D; _ga=GA1.2.1541581907.1558682607; 96b28b766b7e0699aa91c9ff3d890663=aHR0cDovL3RjYWZlMmEuY29tLw%3D%3D; _gid=GA1.2.1287024473.1561011710; cf_clearance=a464dc95d491dc6c78d21f0e89c63c4045208aa1-1561079691-86400-250; PHPSESSID=',
            'Host': 'tcafe2a.com',
            'Pragma': 'no-cache',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
        }
        # ===========================================================================
        # Cloudflare 등등의 사이트에서 userAgent를 사용해서, Bot접속을 차단하고 있음.
        # ===========================================================================
        ua = UserAgent()
        userAgent = ua.random
        self.headers['User-Agent'] = userAgent

        # telegram_token = '5758487515:AAFfZ9fZsv7padX_6StJbn3T9zFOvW46jcc'
        self.bot = telegram.Bot(token = self.telegram_token)
        updates = self.bot.getUpdates()

        # 파이썬 3 항연산자
        self.chat_id = self.telegram_chat_id if len(updates) == 0 else updates[-1].message.chat_id
        self.writeConfig()

    def telegram_bot(self, txt):
        self.bot.sendMessage(chat_id=self.chat_id , text=txt)

    def http_get(self, url):
        response = r.get(url, headers=self.headers)
        return response

    def get_body(self, response):
        encoding = response.encoding
        result = response.text.encode(encoding, "utf-8")
        result = result.decode()
        return result

    def save_source(self, html):
        with open('debug.html','w',encoding="utf-8") as f:
            f.write(html)

    def readConfig(self):
        try:
            self.path = os.path.dirname(os.path.realpath(__file__))
            self.config.read(self.path+'/'+ self.configFile , encoding="utf-8")
            self.tcafe_host = self.config.get('CONFIG','HOST')
            self.tcafe_id = self.config.get('CONFIG','ID')
            self.tcafe_pw = self.config.get('CONFIG','PW')
            self.tcafe_key = self.config.get('CONFIG','KEY')
            self.telegram_token = self.config.get('CONFIG','TELEGRAM_TOKEN')
            self.telegram_chat_id = self.config.get('CONFIG','TELEGRAM_CHAT_ID')
        except:
            filename = self.configFile
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), filename)
            # if os.access(self.configFile,os.F_OK):
            #     os.remove(self.configFile)
            # self.config.add_section('CONFIG')
            # self.config.set('CONFIG','HOST', '')
            # self.config.set('CONFIG', 'ID', '')
            # self.config.set('CONFIG', 'PW', '')
            # self.config.set('CONFIG', 'KEY', '')
            # with open(self.configFile,'w',encoding="utf-8") as f:
            #     self.config.write(f)

    def writeConfig(self):
        if len(self.chat_id) == 0:
            return
        if self.chat_id == self.telegram_chat_id:
            return
        self.config.add_section('CONFIG')
        self.config.set('CONFIG','HOST', self.tcafe_host)
        self.config.set('CONFIG', 'ID', self.tcafe_id)
        self.config.set('CONFIG', 'PW', self.tcafe_pw)
        self.config.set('CONFIG', 'KEY', self.tcafe_key)
        self.config.set('CONFIG', 'TELEGRAM_TOKEN', self.telegram_token)
        self.config.set('CONFIG', 'TELEGRAM_CHAT_ID', self.telegram_chat_id)
        with open(self.configFile,'w',encoding="utf-8") as f:
            self.config.write(f)

    # 1. 나무위키 사이트에서 tcafe 주소를 가져온다.
    # Tcafe 주소가 자주 변경 되므로 자동 찾기를 한다.
    def get_tcafe_domain(self):
        URL = 'https://namu.wiki/w/Tcafe.net'
        xpath = '/html/body/div[2]/article/div[4]/div/div[2]/table/tbody/tr[2]/td[2]/div/a'
        page = r.get(URL)
        # BeautifulSoap 에서는 xpath 를 사용할 수 없다.
        # 그래서 lxml 패키지를 사용하도록 한다.
        tree = html.fromstring(page.content)
        info = tree.xpath(xpath)
        domain = info[0].text
        # self.headers['Referer'] = domain
        if domain.endswith('/'):
            domain = domain[:len(domain)-1]
        return domain

    def start_without_console(self):
        """
        Starts the Service.
        :Exceptions:
         - WebDriverException : Raised either when it can't start the service
           or when it can't connect to the service
        """
        CREATE_NO_WINDOW = 0x08000000
        try:
            cmd = [self.cmd_path]
            if hasattr(self, 'command_line_args'):
                cmd.extend(self.command_line_args())
            self.process = subprocess.Popen(cmd, env=self.env,
                close_fds=platform.system() != 'Windows',
                stdout=self.log_file, stderr=self.log_file, creationflags=CREATE_NO_WINDOW)
            return self.process.returncode
        except TypeError:
            raise

    def invoke(self, cmd):
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        out = subprocess.Popen(cmd, startupinfo=startupinfo
                                    , shell=True
                                    , stdin=subprocess.PIPE
                                    , stdout=subprocess.PIPE
                                    , stderr=subprocess.PIPE
                                    , creationflags=0x08000000).communicate()
        return out

    # ===============================================================================
    # selenium 을 이용한 자동 접속은 google reCaptcha 에 의해 접근이 되지 않는다
    # 그리고 Cloudfare에서 ban 되어 접근조차 할 수 없다. (무엇으로 판단하는 걸까???)
    # 그냥 크롬 브라우저로 접근할 경우 잘 된다.
    # ===============================================================================
    # 참고 자료 : https://beomi.github.io/2017/01/20/HowToMakeWebCrawler-With-Login/
    # ===============================================================================
    def run(self):
        # 1. 나무위키 사이트에서 tcafe 주소를 가져온다.
        # Tcafe 주소가 자주 변경 되므로 자동 찾기를 한다.
        # URL_TCAFE = self.get_tcafe_domain()
        URL_TCAFE = self.tcafe_host
        debug = self.logging.debug
        error = self.logging.error

        # / 페이지에는 reCaptcha 기능이 되어 있으므로, 별도의 다른 페이지로 접근하도록 한다.
        # reChapcha 기능이 있는 페이지로 접근해서는 안된다.
        LOGIN_PAGE=URL_TCAFE+"/bbs/login.php"
        req = self.http_get(LOGIN_PAGE)
        debug(str(req.ok))

        with r.Session() as session:

            if not req.ok:
                reason = str(req.status_code) + ' ' + req.reason
                msg = reason + ' #ERROR# 로그인 페이지 접근 실패!!'
                error(msg)
                self.telegram_bot(msg)
                return

            res = self.get_body(req)
            # print(res)

            debug('===== 접속하기 ======')
            # debug(req.text)

            # 2. 로그인 하기
            LOGIN_CHECK = URL_TCAFE+'/bbs/login_check.php'
            LOGIN_INFO = {}
            LOGIN_INFO['mb_id'] = self.tcafe_id
            LOGIN_INFO['mb_password'] = self.tcafe_pw
            LOGIN_INFO['url'] = 'https://tcafe2a.com/'
            req = session.post(LOGIN_CHECK, headers=self.headers, data=LOGIN_INFO, verify=False)
            if not req.ok:
                reason = str(req.status_code) + ' ' + req.reason
                msg = reason+' #ERROR# 로그인 실패!!'
                error(msg)
                self.telegram_bot(msg)
                return

            html = self.get_body(req)
            # print(html)
            self.save_source(html)

            debug('===== 로그인 완료 ======')
            # debug(req.text)

            # 3. 출첵 페이지로 이동
            PAGE = URL_TCAFE + '/community' + '/attendance'
            req = session.get(PAGE)
            if not req.ok:
                reason = str(req.status_code) + ' ' + req.reason
                msg = reason + ' #ERROR# 출첵 페이지 접근 실패!!'
                error(msg)
                self.telegram_bot(msg)
                return

            html = self.get_body(req)
            self.save_source(html)

            soup = BeautifulSoup(html,"html.parser")
            hidden_tags = soup.find_all('input', {'type':'hidden'})
            for ele in hidden_tags:
                name = ele.get('name')
                value = ele.get('value')
                if name == "secdoe":
                    secdoe = value
                if name == "proctype":
                    proctype = value

            print(secdoe, proctype)

            debug('===== 출첵 이동 ======')
            # debug(req.text)

            # 4. 출첵 버튼 클릭하기
            param = {}
            param['secdoe'] = secdoe
            param['proctype'] = proctype
            # param['url'] = 'https://tcafe2a.com/'

            PAGE = URL_TCAFE + '/attendance' + '/selfattend2_p.php'
            req = session.post(PAGE, data=param)
            if not req.ok:
                reason = str(req.status_code) + ' ' + req.reason
                msg = reason + ' #ERROR# 출첵 버튼 클릭 실패!!'
                error(msg)
                self.telegram_bot(msg)
                return

            html = self.get_body(req)
            self.save_source(html)

            debug('===== 출첵 버튼 클릭 ======')
            # debug(req.text)

            debug('===== 출첵 완료 검사 ======')
            # fix : TypeError: expected string or bytes-like object
            txt = re.compile(r'출석.*주세요|출석.*획득').findall(html)
            msg = '출석 확인 필요합니다.' if len(txt) == 0 else ''.join(txt)
            msg = BeautifulSoup(msg, "html.parser").text # html태그 제거(xml 구조 오류가 있어도 무시하고 파싱처리 됩니다. 단 처리속도가 다소 늦습니다.)
            debug(msg)
            self.telegram_bot(msg)

if __name__ == '__main__':
    attandance = AutoTcafe()
    # with contextlib.redirect_stdout(io.StringIO()):
    attandance.run()
