# 거북이로 장미 그리기
# %%

import turtle

# 설정
t = turtle.Turtle()
t.speed(0)  # 최대 속도

# 장미 꽃잎 그리기 함수
def draw_petal():
    t.color("red")
    t.begin_fill()
    t.circle(50, 60)
    t.left(120)
    t.circle(50, 60)
    t.left(120)
    t.end_fill()

# 장미 그리기
for _ in range(6):
    draw_petal()
    t.right(60)

# 줄기 그리기
t.color("green")
t.right(90)
t.forward(200)

# 잎사귀 그리기
t.right(45)
t.color("green")
t.begin_fill()
t.circle(50, 90)
t.left(90)
t.circle(50, 90)
t.end_fill()

# 다른 잎사귀 그리기
t.left(135)
t.forward(100)
t.left(45)
t.begin_fill()
t.circle(50, 90)
t.left(90)
t.circle(50, 90)
t.end_fill()

# 완료
turtle.done()

