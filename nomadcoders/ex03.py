# 파이썬을 이용한 class adbUtils 만들기
# adb를 이용한 좌표값 x, y 에 대한 colorpicker 기능 구현

'''
설명:
OpenCV 사용:

PIL 대신 OpenCV를 사용하여 이미지를 처리합니다. OpenCV는 고성능 이미지 처리 라이브러리로, 특히 대규모 이미지 데이터에 대해 더 빠른 성능을 제공합니다.
np.frombuffer와 cv2.imdecode를 사용하여 ADB로부터 받은 이미지 데이터를 OpenCV 이미지 형식으로 변환합니다.
메모리 해제:

이전 스크린샷이 있다면 del self.screenshot을 통해 명시적으로 메모리를 해제합니다.
색상 추출:

OpenCV는 기본적으로 BGR 포맷을 사용하므로, 이를 RGB 포맷으로 변환하여 반환합니다.
이 최적화된 코드는 멀티 스레드 환경에서 더 빠르고 효율적으로 스크린샷을 캡처하고 처리할 수 있도록 합니다.
'''

import subprocess
import numpy as np
import cv2
import time
import threading

class adbUtils:
    def __init__(self, adb_path='adb'):
        self.adb_path = adb_path
        self.screenshot = None
        self.lock = threading.Lock()

    def _run_adb_command(self, command):
        result = subprocess.run([self.adb_path] + command.split(), capture_output=True)
        if result.returncode != 0:
            raise Exception(f"ADB command failed: {result.stderr.decode()}")
        return result.stdout

    def capture_screenshot(self):
        with self.lock:
            # 이전 스크린샷이 있다면 메모리 해제
            if self.screenshot is not None:
                del self.screenshot
            
            # 새로운 스크린샷 캡처 및 메모리 로드
            screenshot_data = self._run_adb_command('exec-out screencap -p')
            np_img = np.frombuffer(screenshot_data, np.uint8)
            self.screenshot = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    def get_color_at(self, x, y):
        with self.lock:
            if self.screenshot is None:
                raise Exception("Screenshot not captured yet.")
            # OpenCV의 BGR 포맷을 RGB로 변환
            b, g, r = self.screenshot[y, x]
            return (r, g, b)

# 사용 예제
adb = adbUtils()

def capture_and_get_color(thread_id):
    for i in range(5):
        start_time = time.time()
        adb.capture_screenshot()
        print(f"Thread {thread_id}: Screenshot {i+1} captured in {time.time() - start_time:.2f} seconds")

        # 특정 좌표의 색상 추출
        color = adb.get_color_at(100, 200)
        print(f"Thread {thread_id}: Color at (100, 200): {color}")

# 여러 스레드 생성 및 실행
threads = []
for i in range(3):  # 3개의 스레드 예제
    t = threading.Thread(target=capture_and_get_color, args=(i,))
    threads.append(t)
    t.start()

# 모든 스레드가 종료될 때까지 대기
for t in threads:
    t.join()