
'''
# -----------------------------
# 거짓인 경우
# -----------------------------
None: 값이 없음을 나타냅니다.
0: 정수형 0.
0.0: 부동소수점형 0.
0j: 복소수형 0.
False: 불린형 거짓 값.
빈 문자열: "" (길이가 0인 문자열). ''
빈 리스트: [].
빈 튜플: ().
빈 딕셔너리: {}.
빈 세트: set().
range(0): 길이가 0인 range 객체
'''

'''
0123456789 출력하기
count = 0
while count < 10: # 참 일경우에만 동작함
    print(count, end='')
    count = count + 1
print('')

# --------------------------
i = 0
while True:
    if i % 3 == 0:
        print(i)
    i += 1 # i = i + 1 와 같은 식임
    if i == 10:
        break
와 결과가 같음.
for i in range(0, 10, 3):
    print(i)
'''

## 짝수인 경우만 출력
count = 0 
while count < 10:
    if count % 2 == 0:
        print(count)
    count += 1

import random
def rand():
    return random.randint(0, 2)

while rand():
    print('하하하')

# %%
# 리스트 처리 (변경 가능하다, 어떤 타입의 자료형도 올 수 있다)
# len 의 사용법을 외워라.
# 배열은 [0: len(배열)-1] 까지를 다루게 된다.
my_list = ['a',True,0.3, None, (2,4,5), ['A', 'B']]
#           -- ---  ---  ----  -------  ----------
#           0   1    2    3      4          5
print(my_list)

# 맨앞에 추가하기
my_list.insert(0, 'APPLE')
print(my_list)

# 가운데 위치 알아오기
center = len(my_list)//2
my_list.insert(center,'BANANA')
print(my_list)

# 몇개는 어떻게 알지?
print(len(my_list))

# a, True 만 출력하기 : 슬라이싱 [start: to(미만): step]
print(my_list[0:2])

# ['A', 'B']만 출력하시오. (실패, my_list가 바뀌어서)
print(my_list[5])

last = len(my_list)-1 # 배열의 맨 마지막 항목
print(my_list[last])

# 질문: 그러면 배열의 가장 첫번째 항목은?

# 변경하기
my_list[1] = 'b'
print(my_list)

# 'BANANA' 지우기
my_list.remove('BANANA')
print(my_list)

# 'APPLE' 지우기
del my_list[0]
print(my_list)

# 맨 뒤에 추가하기
my_list.append(3)
my_list.append(4)
my_list.append(5)
print(my_list)

# %%
# 로켓발사 할 때 카운트 다운. 10, 9, ... 0
# 시작값은 10
# 한번에 하락하는 값 -1
# 반복횟수 11번
import time
for i in range(10, -1, -1):  # 범위()
    print(i)
    time.sleep(1) # 1초 쉬기
print('땡! 발사!!!')

# 딕셔너리 만들기
# (비딩-키워드하는데 사전처럼 사용)
# 키(key):값(value)  자료형 key => k, value = v
# %%
my_dict = {'flower' :'꽃'
        , 'tree':'나무'
        , 'board': '보드'
        , 'apple':'사과'
        , 'key':'열쇠'
        , 'banana':'바나나'
        , 'student':'학생'
        , 'cat':'고양이'
        , 'weather':'날씨'
        , 'rain':'비'}

print('사전갯수 : '+str(len(my_dict)) + '개') # 문자열만 출력해야 해서 str 형변환함
print(list(my_dict.keys()))  # 키만 출력하기.
print(list(my_dict.values()))  # 키로해서 값을 뽑아내기.

# %%

# values() 를 구현하기
values = [] # 빈 배열로 초기화
for k in my_dict.keys(): # 사전형에서 키값들만 가져오기
    v = my_dict[k] # 사전형에서 값을 가져오기
    values.append(v) # 해당 값을 values 배열에 담기
print(values) # 배열 출력하기


# %%
for i in range(5) : # 5 번만 실행한다.
    word = input("영단어를 입력하세요.==> ") # 문자열을 입력받는다.
    if word in my_dict.keys() : # keys(), values() 가 있다.
        print(word, ":", my_dict[word]) # 뜻을 찍어라.
    else :
        print("사전에 없는 단어 입니다. 무식한 넘, 기회한번 차감이다.")

# '''
# while 문으로 
my_dict = {'flower':'꽃', 'tree':'나무', 'boare': '보드', 'apple':'사과', 'key':'열쇠', 'banana':'바나나', 'student':'학생', 'cat':'고양이', 'weather':'날씨', 'rain':'비'}
while True : # 무한루프
    word = input("찾는 단어는? ")

    if word in my_dict.keys() : # in 을 사용해서 찾기
        mean = my_dict[word] # key에 해당하는 값을 가져오기
        print(word, ":", mean)

    quit = input("계속할까요? (y/n) ")
    if quit == 'n' :
        break

    print('바붕~ 다시 찾아봐바. 영원히')

# %%
# in 이 뭘까요? 배열안에서 찾아주기
arr = ['a','b']
if '1' in arr : # 있으면 참, 없으면 거짓
    print("있어유")
else:
    print("없어유")

# %%
# 리스트를 딕셔너리로 변환 # 시험 범위 밖
keys = ['a', 'b', 'c'] # 배열
values = [1, 2, 3] # 배열

# zip을 사용하여 딕셔너리 생성
my_dict = dict(zip(keys, values))
print(my_dict)  # 출력: {'a': 1, 'b': 2, 'c': 3}

# 사전형을 리스트로 변환하기
# 딕셔너리에서 키와 값을 리스트로 변환
my_dict = {'a': 1, 'b': 2, 'c': 3}

# 키 리스트
# %%
keys_list = list(my_dict.keys())
print(keys_list)  # 출력: ['a', 'b', 'c']

# 값 리스트
values_list = list(my_dict.values())
print(values_list)  # 출력: [1, 2, 3]

# 딕셔너리를 튜플로 변환
my_dict = {'a': 1, 'b': 2}

# 튜플로 변환
dict_items = tuple(my_dict.items())
print(dict_items)  # 출력: (('a', 1), ('b', 2))
# %%
my_test = [1, 2, 3, 4, 5]
while my_test:
    print(my_test.pop())

# %%
my_test = [1, 2, 3, 4, 5]
print(my_test)
my_test.append(6) # 뒤에서 부터 추가
my_test.pop() # 뒤에서 부터 제거
print(my_test)

# %%
a = 'abcdef' # 문자열은 문자의 연속적인(순서가정해진) 집합 => 배열이므로
# ---012345------
print(a[2:4]) # 'cd' 배열처럼 처리 가능하다. 슬라이싱이라고 한다.

# %%
'''
소수점 자리수 제한
round()는 반올림 함수
'''
a = 5 / 3
b = 2 / 3
# .자리수f => 소수점 자리수 제한 표현
print('%f, %.3f, %.2f, %.2f' % (a, a, round(a, 2), b))
# 결과값 : 1.666667, 1.667, 1.67, 0.67
# %%
