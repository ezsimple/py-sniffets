# -*- coding:utf-8 -*-
__author__ = "mkeasy@gmail.com"

import os
import sys
import time
import shutil
import subprocess
import threading
# import ctypes
# import win32gui
# import win32console

printf = sys.stdout.write


class DevelEnv(threading.Thread):
    '''
    개발에 필요한 무설치 개발도구들을 실행 시킨다
    '''

    def __init__(self, args):
        threading.Thread.__init__(self, args=(args,), daemon=True)
        self.args = args
        # print(args)
        pass

    def invoke(self, cmd):
        return os.popen(cmd).readlines()

    def winvoke(self, cmd):
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        out, err = subprocess.Popen(cmd, startupinfo=startupinfo, shell=True, stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        if b'device not found' in err:
            raise Exception
        return out

    def run(self):
        # localhost:80
        if self.args == 'apache':
            cmd = r'cd C:\Tools\Apache24\bin && httpd.exe'

        # localhost:9200
        if self.args == 'elasticsearch':
            cmd = r'cd C:\Tools\elasticsearch-7.8.1\bin && elasticsearch.bat'

        # localhost:5601
        if self.args == 'kibana':
            cmd = r'cd C:\Tools\kibana-7.8.1-windows-x86_64\bin && kibana.bat'

        # localhost:9600
        if self.args == 'logstash':
            cmd = r'cd C:\Tools\logstash-7.8.1\bin && logstash.bat -f ..\config\logstash_eggplan.conf'

        # localhost:3000
        if self.args == 'grafana':
            cmd = r'cd "C:\Tools\grafana-7.1.1\bin" && grafana-server.exe'

        # none
        if self.args == 'filebeat':
            cmd = r'cd "C:\Tools\filebeat-7.8.1-windows-x86_64" && filebeat.exe -c filebeat.yml'
        
        # mongoDB
        if self.args == 'mongodb':
            cmd = r'cd "C:\Tools\mongodb-win32-x86_64-windows-4.4.5\bin" && mongod.exe --dbpath "C:\Tools\mongodb-data" --journal --bind_ip 127.0.0.1 --logpath "C:\Temp\mongod.log"'

        print('start '+cmd)
        self.winvoke(cmd)


if __name__ == "__main__":
    threads = []

    threads.append(DevelEnv('apache'))
    threads.append(DevelEnv('elasticsearch'))
    threads.append(DevelEnv('kibana'))
    threads.append(DevelEnv('filebeat'))
    # threads.append(DevelEnv('logstash'))
    # threads.append(DevelEnv('grafana'))
    threads.append(DevelEnv('mongodb'))

    for i, v in enumerate(threads):
        v.start()

    for i, v in enumerate(threads):
        v.join()

    # 콘솔창을 최소화 (그냥 보이는게 낫다)
    # ctypes.windll.user32.ShowWindow( ctypes.windll.kernel32.GetConsoleWindow(), 6 )
    # win32gui.ShowWindow(win32console.GetConsoleWindow(), 0)

    pass
