# -*- coding: utf-8 -*-
import logging
import os
from time import strftime, localtime

class LogUtil:

    def __init__(self, prefix=None):

        # 현재 디렉토리에 log 폴더가 없으면 생성 합시다.
        path = os.getcwd()+"\\log"
        if not os.path.exists(path):
            os.mkdir(path)

        PREFIX_LOG = 'homm_logging'
        if prefix:
            PREFIX_LOG = str(prefix)

        today = strftime("%Y-%m-%d", localtime())
        filename = path + '\\' + PREFIX_LOG +'-' + str(today)+'.log'

        # 파일에 새로운 내용이 추가(append) 됩니다.
        handlers = [logging.FileHandler(filename=filename, mode='a', encoding='utf-8')]
        logging.basicConfig(handlers=handlers,format='[%(levelname)s] %(message)s',level=logging.DEBUG)

    # ----------------------------------------------------------------
    # 쓰레드에서 GUI를 바로 접근할 수 없다.
    # Make sure 'QTextCursor' is registered using qRegisterMetaType().
    # ==> 당연한건데... ㅋ , 시그널을 사용해야 한다.
    # ----------------------------------------------------------------

    # def toTextEdit(self, text):
    #     with self.app.lock:
    #         if self.app.textEdit:
    #             #cursor = self.app.textEdit.textCursor()
    #             cursor = QTextCursor(self.app.textEdit.document())
    #             cursor.movePosition(QtGui.QTextCursor.End)
    #             cursor.insertText(text)
    #             self.app.textEdit.moveCursor(QtGui.QTextCursor.End)
    #             # self.textEdit.setTextCursor(cursor)
    #             # self.textEdit.ensureCursorVisible()

    def error(self, text):
        now = strftime("[%H:%M:%S] ", localtime())
        logging.error(now + text)

    def debug(self, text):
        now = strftime("[%H:%M:%S] ", localtime())
        logging.debug(now + text)


