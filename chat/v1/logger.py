# logging.py
import os
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

class LoggerSetup:
    def __init__(self, log_dir="log"):
        self.log_dir = log_dir
        self.logger = logging.getLogger(__name__)
        self.setup_logging()

    def setup_logging(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        log_path = os.path.join(current_dir, self.log_dir)
        os.makedirs(log_path, exist_ok=True)  # log 디렉토리가 없으면 생성

        current_date = datetime.now().strftime("%Y-%m-%d")
        log_file_name = f"{os.path.basename(__file__)}-{current_date}.log"
        log_file_path = os.path.join(log_path, log_file_name)

        handler = TimedRotatingFileHandler(log_file_path, when="midnight", interval=1, backupCount=7)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(filename)s - line:%(lineno)d - %(message)s'))

        logging.basicConfig(
            level=logging.WARNING,  # 기본 로깅 레벨을 WARNING으로
            handlers=[
                handler,
                logging.StreamHandler()  # 콘솔에도 로그 출력
            ]
        )
        self.logger.setLevel(logging.DEBUG)  # 현재 인스턴스의 로거를 DEBUG 레벨로 설정

    def get_logger(self):
        return self.logger
