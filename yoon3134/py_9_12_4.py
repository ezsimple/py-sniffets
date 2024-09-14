'''
24.09.12 파이썬 강의 소스
거북이 그리기 - 바람개비 그리기
'''
# %%
import turtle as t

t.bgcolor("blue")
t.color("white")
t.speed(3000)

for x in range(250):

  t.fd(x)
  t.rt(89)
