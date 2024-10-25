# %%
name = '홍길동'
age = 30
# string => %s 
# integer => %d
# float => %f

my_list = [1, 2, 3]
print("리스트:", my_list)

# %%
a = 1
b = 2
print (a<=b)

# %%

print('\t지윤이')
print('\t\b지윤이')

# %%
a = 1
a = 2 ** 2
print(a)

# %%
def mux(a, b):
    return a, b, b * 2

print(mux(('a'), 3))

# %% 

a = 1

# 선언
def varTest():
    a = 2
    print(a)

# 선언
def varTest2():
    a = 3
    print(a)

varTest()
# %%


x = ''
if x:
    pass
else:
    print('거짓')

# %% 
for i in range(10):
    if i % 2 == 0:
        print(i)

# %% 
def dladkladjfa():
    pass

dladkladjfa()

# %% 
squares = [x**2 for x in range(10)]
print(squares)

# %%
# 함수를 왜???? 만들어????
def even(max = 10):
    print([x for x in range(max) if x % 2 == 0])

even(100)

# %%
def min_max(numbers):
  return min(numbers), max(numbers)
    
low, high = min_max([1, 2, 3, 4, 5])

low, high = (1, 100) # unpack
print(low, high)

# %%
# import random

ss = "AAAABBBCCDDEEBB"
index = ss.find('BB')
index = ss.find('BB', index + 1)
index = ss.find('BB', index + 1)
print(index)

# %%
for i in range(5):
    v = input('대문자를 넣으세요')
    if v.isupper():
        print('참잘했어요')
        print(v.count('A'))
    else:
        print('다시 넣으세요')


# %%
print(0 / 1)

# %%
print(0 == 0.0)

# %%
print(bool(""))

# %%
# 조건방정식
a = 7
b = 2
if 0 == 0.0:
    print("참")