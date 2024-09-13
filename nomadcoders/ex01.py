# %%
from pydantic import BaseModel, Field

class Movie(BaseModel):
    a :str = Field(min_length=2, max_length=8)
    b :int = 2
    c :int

    @staticmethod
    def print(cls, *values: object) -> None:
        print(values)

data = {
    'a': '111',
    'b': 2,
    'c': 5
}

tmp = Movie(**data)
Movie.print('hello', tmp, 1, 2, 3)


# %%
# 메모이제이션 & 재귀호출을 통한 쿠폰번호 고속 처리
import random
import string
import time
from datetime import timedelta

def generate_coupon(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def generate_unique_coupon(existing_coupons, length=8):
    new_coupon = generate_coupon(length)
    if new_coupon in existing_coupons:
        return generate_unique_coupon(existing_coupons, length)  # 재귀 호출
    existing_coupons.add(new_coupon)
    return new_coupon

def measure_exec_time(start_time: float, end_time: float) -> None:

    # 소요 시간 계산
    elapsed_time = end_time - start_time

    # 소요 시간을 timedelta 객체로 변환
    elapsed_timedelta = timedelta(seconds=elapsed_time)

    # timedelta 객체를 일, 시, 분, 초, 밀리초로 변환
    days = elapsed_timedelta.days
    seconds = elapsed_timedelta.seconds
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = elapsed_timedelta.microseconds // 1000

    # 출력할 시간 구성 요소와 값을 튜플로 묶기
    time_components = [
        (days, "일"),
        (hours, "시"),
        (minutes, "분"),
        (seconds, "초"),
        (milliseconds, "밀리초")
    ]

    # 조건에 따라 문자열을 구성
    result = " ".join(f"{value}{unit}" for value, unit in time_components if value > 0)

    # 결과 출력
    print(f"소요 시간: {result}")


# 예시
existing_coupons = set()
start_time = time.time()
for _ in range(1000000):
    print(generate_unique_coupon(existing_coupons))
end_time = time.time()

measure_exec_time(start_time=start_time)


# 생성된 쿠폰 번호를 확인합니다.
# print(existing_coupons)
print(len(existing_coupons))
