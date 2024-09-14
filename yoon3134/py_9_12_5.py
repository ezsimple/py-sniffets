'''
24.09.12 파이썬 강의 소스
거북이 그리기 - 링으로 원 그리기
'''
# %%
import turtle as t

t.bgcolor("black")
t.color("violet")
t.speed(300)

for x in range(50):

  t.circle(70*2)
  t.lt(360/50)

 

