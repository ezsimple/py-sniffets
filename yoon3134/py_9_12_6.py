'''
24.09.12 파이썬 강의 소스
거북이 그리기 - 태극 문양 그리기
'''
# %%
import turtle as t

t.bgcolor("black")
t.speed(0)

for  x  in  range(250):

  if x %3 ==1:
    t.color("red")

  if x %3 ==1:
    t.color("yellow")

  if x %3 ==2:
    t.color("blue")


  t.fd(x*2)
  t.left(119)
