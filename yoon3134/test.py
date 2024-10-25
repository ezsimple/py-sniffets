# %%
a = 'lee\tjiyoon'
b = [1,2,3,4]
c = [10,9,8,'abc']

d = 123456
print(d,str(d))
for i in range(1,10) :
    if i % 2 == 1 :
        print(i)
#%%
s=0
for i in range(1, 11) :
    #i -> 12345..10
    s += i

print(s)
#%%

num = 10.88529293993939
# print(f"{num:0.2f}")
print("%0.2f" % num)

# %%
num = 10.99172947239797349
print("%04d" % num)


# %%
# 슬라이싱 : 시작부터 미만까지
my_list = [1, 2, 3]
print(my_list[:1])

# %%
# 사전형 : {k: v, k1: v1, k2: v2, ...} 키:값의 쌍으로 구성, 키로 값을 찾음, 순서 없음
my_dict = {"이름": "홍길동", "나이": 30, "주소": "부천"}
print("이름:", my_dict["이름"], "나이:", my_dict["나이"], "주소:", my_dict['주소'])

# %%
name = "홍길동"
age = 30
print("이름: {}, 나이: {}".format(name, age))

# %%
name = "홍길동"
age = 30
print(f'이름: {name}, 나이: {age}')

# %%
print("안녕하세요.", end="")
print("반갑습니다.")
print("또 반갑습니다.")

# %%
print("첫 번째 줄\n두 번째 줄")

# %%
'''
| 할당연산자       |                | 비교연산자      |       |     |
| ----------- | -------------- | ---------- | ----- | --- |
| 할당하기        | =              | 같다         | ==    |     |
| 사칙 연산 결과 저장 | +=, -=, *=, /= | 다르다        | !=    |     |
| 몫, 나머지 저장   | //=, %=        | 크다, 크거나 같다 | >, >= |     |
| 거듭 제곱값 저장   | **=            | 작다, 작거나 같다 | <, <= |     |
'''
def 함수이름(파라미터1=1, 파라미터2=2):
  # 수행할 작업
  return 결과

def add(a, b):
  return a + b

sum = add(1, 3)
print(sum)  

# %%
def greet(name="손님"):
  return f"안녕하세요, {name}!"

welcome = greet("지윤님")
print(welcome)

# %%
def square(x):
  return x * x # 단일 리턴 값

def min_max(numbers):
  return max(numbers), min(numbers) # 다중 리턴 (튜플)

# (,,,,,) vs [,,,,,,], {k:v, k1:v1, k2:v3}, 'abc', "defg" 

a, b = min_max((1, 2, 3, 4, 10, 5, 11))
print(a, b)
# %%
a = 1 # 전역변수

def 함수1():
    a = 2 # 지역변수

    def 함수2():
        print(a)
    
    함수2()

함수1()

# %%
for i in range(10): # 0 <= i < 10, 
    if i % 2 == 1:
        break
    print(i)

print("반복문 종료")
    
# %%
# boolean
# 문자열 : 글자의 순서를 가진 연속적인 배열 
a = '12345'
print(a[1:3]) # 인덱스가 1부터 3미만인 값


# %%
a = 0
b = 1
if a > 1 and a < 10 and b == 1:
    print('a는 1보다 크고 10보다 작다.')

# %%
a = 0
a += 1 # a = a + 1
print(a)

# %%
q = 3.14
print("%f, %d, %.2f" % (q, q, q))