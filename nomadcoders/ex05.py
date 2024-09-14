'''
거북이 그리기 - 장미 그리기
'''
from turtle import Turtle, Screen, TurtleScreenBase
import sys

t = Turtle()
t.shape('turtle')
t.speed(0)
t.color('pink')

# 펜을 들어서, x,y 좌표로 이동하기
t.penup()
t.goto(x=0, y=200)
t.pendown()

# 배경설정
s = Screen()
s.bgcolor("black")

# 꽃잎그리기
for i in range(200):
    t.pensize(i/50)
    t.forward(i)
    t.left(65)

# 줄기그리기
t.color('lightblue')
t.setheading(270)

for i in range(50):
    t.pensize(25 - i/2)
    t.forward(i/4)

# 잎그리기
t.color('yellowgreen')
t.setheading(60)
for i in range(100):
    t.pensize(100 - i)
    t.forward(i/10)

# 마지막으로 거북이를 숨긴다.
t.hideturtle()

def wait_for_quit(s : TurtleScreenBase):
    # q 또는 스페이스를 입력하거나, 마우스 클릭이 발생하면 스크린을 닫는다.
    s.onkey(lambda: sys.exit(), "q")
    s.onkey(lambda: sys.exit(), " ")
    s.onclick(lambda x, y: sys.exit())
    s.listen()
    s.mainloop()

wait_for_quit(s)