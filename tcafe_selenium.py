# -*- coding: utf-8 -*-

# ==================================
# tcafe 자동 출석 체크하는 프로그램
# ==================================
# 좋은 소스가 있네요. 공부합시다.
# https://github.com/lumyjuwon/NaverCaptcha
# ==================================

import configparser
import contextlib
import ctypes
import io
import os
import platform
import subprocess
import errno

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import staleness_of
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from lxml import html
import requests
from fake_useragent import UserAgent

# from win32process import CREATE_NO_WINDOW

class TcafeAttandance:

    def __init__(self):
        self.config = configparser.RawConfigParser()
        self.configFile = 'tcafe_config.ini'
        self.readConfig()
        pass

    # 페이지 로딩을 감지하는 클래스 (페이지간 이동(링크) 처리를 보다 빠르게 처리하도록 합시다)
    # http://www.obeythetestinggoat.com/how-to-get-selenium-to-wait-for-page-load-after-a-click.html

    # 시험중....
    # 페이지가 계속 로딩중인 상태, 그러나 컨텐츠는 보이는 상태.
    # ESC를 입력해서 로딩을 멈춘후, 이후 작업을 빠르게 진행한다.
    # def sendESC(self):
    #     # self.browser.find_element_by_tag_name('body')[0].sendKeys('Keys.ESCAFE')
    #     try:
    #         self.browser.getPageSource()
    #     except Exception as e:
    #         print(e)
    #         return False
    #     self.browser.find_element_by_tag_name('body')[0].sendKeys('Keys.ESCAFE')
    #     return True

    @contextlib.contextmanager
    def wait_for_page_load(self, timeout=30):
        old_page = self.browser.find_element_by_tag_name('html')
        yield
        WebDriverWait(self.browser, timeout).until(
            staleness_of(old_page)
        )

    def readConfig(self):
        try:
            self.path = os.path.dirname(os.path.realpath(__file__))
            self.config.read(self.path+'/'+ self.configFile , encoding="utf-8")
            self.tcafe_host = self.config.get('CONFIG','HOST')
            self.tcafe_id = self.config.get('CONFIG','ID')
            self.tcafe_pw = self.config.get('CONFIG','PW')
            self.tcafe_key = self.config.get('CONFIG','KEY')
        except:
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

    def ok_allow(self):
        URL = 'http://cloud.mkeasy.kro.kr:8800/allow/tcafe/check'
        data = {'key':self.tcafe_key}
        r = requests.post(URL, json=data, verify=False)
        if r.status_code != 200:
            raise SystemExit('This program is no longer available.')

    # 1. 나무위키 사이트에서 tcafe 주소를 가져온다.
    # Tcafe 주소가 자주 변경 되므로 자동 찾기를 한다.
    def get_tcafe_domain(self):
        URL = 'https://namu.wiki/w/Tcafe.net'
        xpath = '/html/body/div[2]/article/div[4]/div/div[2]/table/tbody/tr[2]/td[2]/div/a'
        page = requests.get(URL)
        # BeautifulSoap 에서는 xpath 를 사용할 수 없다.
        # 그래서 lxml 패키지를 사용하도록 한다.
        tree = html.fromstring(page.content)
        info = tree.xpath(xpath)
        domain = info[0].text
        return domain

    # def start_without_console(self):
    #     """
    #     Starts the Service.
    #     :Exceptions:
    #      - WebDriverException : Raised either when it can't start the service
    #        or when it can't connect to the service
    #     """
    #     try:
    #         cmd = [self.cmd_path]
    #         if hasattr(self, 'command_line_args'):
    #             cmd.extend(self.command_line_args())
    #         self.process = subprocess.Popen(cmd, env=self.env,
    #             close_fds=platform.system() != 'Windows',
    #             stdout=self.log_file, stderr=self.log_file, creationflags=CREATE_NO_WINDOW)
    #         return self.process.returncode
    #     except TypeError:
    #         raise

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

    def run(self):
        # self.ok_allow()

        # 1. 나무위키 사이트에서 tcafe 주소를 가져온다.
        # Tcafe 주소가 자주 변경 되므로 자동 찾기를 한다.
        # URL_TCAFE = self.get_tcafe_domain()
        URL_TCAFE = self.tcafe_host;

        #
        # https://github.com/pyinstaller/pyinstaller/wiki/Recipe-subprocess
        # import sys
        # if sys.platform == "win32":
        #     import ctypes
        #     ctypes.windll.kernel32.SetDllDirectoryA(None)
        # 2. 윈도우의 콘솔창을 숨긴다.
        # ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

        # 3. 크롬 드라이버 실행하기
        path = os.path.dirname(os.path.realpath(__file__))
        driver_cmd = path+'\\chromedriver.exe'

        # 실행시 console 창이 생기지 않도록 webdriver 소스 수정
        # D:\Anaconda3\envs\venv3.5\Lib\site-packages\selenium\webdriver\common\service.py
        args = ["hide_console", ]

        # # Headless 탐지 막기
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox"); # Bypass OS security model, must use first
        # options.add_argument('headless')
        # userAgent = '--user-agent="Mozilla/5.0 (Windows Phone 10.0; Android 4.2.1; Microsoft; Lumia 640 XL LTE) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Mobile Safari/537.36 Edge/12.10166"'

        # whale browser 의 userAgent 입니다. (주소줄에 about: 입력하면 알수 있습니다)
        #userAgent = '--user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Whale/1.5.72.5 Safari/537.36"'
        ua = UserAgent()
        userAgent = ua.random
        print("userAgent : ",userAgent);
        userAgent = '--user-agent='+userAgent
        options.add_argument(userAgent)
        # options.add_argument('disable-gpu')
        # remove "chrome is being controlled by automated test software"
        # 제거 : "크롬이 자동화된 테스트 소프트웨어에 의해 제어되고 있습니다"
        options.add_argument("disable-infobars");

        # 하 ... 셀레니움에 플러그인 추가도 일이구나....
        # extentions_dir = 'C:/Users/mkeas/AppData/Local/Google/Chrome/User Data/Default/Extensions/Extensions\mpbjkejclgfgadiemmefgebjfooflfhl'
        # options.add_argument(r'--load-extension=C:\Users\mkeas\AppData\Local\Google\Chrome\User Data\Default\Extensions\Extensions\mpbjkejclgfgadiemmefgebjfooflfhl')
        # user_data = r'--user-data-dir=C:\Users\mkeas\AppData\Local\Naver\Naver Whale\User Data\Profile 1'
        # user_data = r'--user-data-dir=C:\Users\mkeas\AppData\Local\Google\Chrome\User Data\Default'
        # options.add_argument(user_data)

        # 하.... 웨일로 실행할 수 없다... ㄷㄷㄷ
        # whale  = r'C:\Program Files (x86)\Naver\Naver Whale\Application\whale.exe'

        # 이렇게 크롬을 지정하는건 의미가 없는 것 같다. (그러나 실행은 된다)
        # chrome = r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
        # options.binary_location = chrome

        self.browser = webdriver.Chrome(executable_path=driver_cmd, service_args=args, options=options)
        # self.browser = webdriver.Remote('http://127.0.0.1:4444/wd/hub', options.to_capabilities())
        self.browser.set_window_rect(0,0,800,450)
        self.browser.implicitly_wait(1)

        # 4. Tcafe 사이트 접속하기
        LOGIN_PAGE = URL_TCAFE + "bbs/login.php"
        self.browser.get(LOGIN_PAGE)
        # self.sendESC()
        # reCaptcha를 해결해야 한다.
        # 현재 tCafe 사이트에서 자동화 프로그램에 의한 접속을 감지하고 있다.
        # 망할 .... ㅡㅡ;;; 웨일로 접속하면 reCaptcha가 뜨지 않는다.
        # 그런데 웨일 브라우져를 쓸수 없다.

        # 5.reCapcha 해결이 되어야 한다.
        with self.wait_for_page_load(timeout=10):
            # 5. 로그인 하기 (아이디/패스워드 입력하기)
            ID = self.tcafe_id
            PW = self.tcafe_pw
            elem = self.browser.find_element_by_id("mb_id")
            elem.send_keys(ID)
            elem = self.browser.find_element_by_id("mb_password")
            elem.send_keys(PW)
            elem.send_keys(Keys.RETURN)

        # 6. 로그인 팝업창 닫기 필요
        # 7. 출석 확인 페이지로 이동
        page = URL_TCAFE + '/attendance/selfattend2.php'
        self.browser.get(page)
        # self.sendESC()

        # 8. 출석하기 GO 버튼 클릭하기
        try:
            with self.wait_for_page_load(timeout=10):
                xpath = '//*[@id="cnftjr"]/div[1]/form/table/tbody/tr/td/img'
                # xpath를 통해 찾은 결과가 리스트이거나 단일 element일 수 있다.
                button = self.browser.find_elements_by_xpath(xpath)[0]
                button.click()

        except Exception as e:
            #print('이런 문제가 있다고 하네요 : \n', e)
            pass
        finally:
            # 7. 셀레니움 창 닫기
            self.browser.quit()

if __name__ == '__main__':
    attandance = TcafeAttandance()
    with contextlib.redirect_stdout(io.StringIO()):
        attandance.run()
