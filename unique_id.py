#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
import time
import random
import string
import timeit
import uuid

# def generate_unique_id():
#    timestamp = int(time.time())
#    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
#    
#    # 타임스탬프를 문자열로 변환하여 랜덤 부분과 결합합니다.
#    unique_id = f"{random_part}{timestamp}"
#    
#    return unique_id[:10]  # 10자리로 잘라서 반환

def generate_unique_id():
    # UUID를 사용하여 고유 ID 생성
    unique_id = str(uuid.uuid4())  # UUID4를 사용하여 고유한 ID 생성
    return unique_id.replace("-", "")[:10]  # 하이픈 제거 후 10자리로 잘라서 반환

def test_unique_id_generation(iterations=1000000):
    unique_ids = set()  # 고유 ID를 저장할 Set
    for _ in range(iterations):
        new_id = generate_unique_id()
        unique_ids.add(new_id)  # Set에 추가 (중복은 자동으로 무시됨)
    
    # 중복이 발생했는지 확인
    if len(unique_ids) == iterations:
        print("중복값이 발생하지 않았습니다.")
    else:
        print("중복값이 발생했습니다.")

start_time = time.time()  # 시작 시간 기록

# 테스트 실행
execution_time = timeit.timeit('test_unique_id_generation()', globals=globals(), number=1)

# 수행 시간 출력
print(f"수행 시간: {execution_time:.2f}초")

# 예시로 고유 ID 생성
# unique_id = generate_unique_id()
# print(unique_id)
