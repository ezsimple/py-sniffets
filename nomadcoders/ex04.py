# 거북이로 장미 그리기
# %%
import turtle
import random
import time

def draw_petal(t):
    t.color("red")
    t.begin_fill()
    t.circle(50, 60)
    t.left(120)
    t.circle(50, 60)
    t.left(120)
    t.end_fill()

def draw_rose():
    # 설정
    t = turtle.Turtle()
    t.speed(0)  # 최대 속도
    # 장미 그리기
    for _ in range(6):
        draw_petal(t)
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

def draw_mandala():
    screen = turtle.Screen()
    screen.bgcolor("black")

    mandala = turtle.Turtle()
    mandala.speed(0)  # 최대 속도

    colors = ["red", "yellow", "blue", "green", "purple", "orange", "white", "cyan"]

    def draw_circle(radius):
        mandala.circle(radius)

    def draw_pattern():
        for _ in range(36):  # 10도씩 회전하며 36번 그림
            mandala.color(random.choice(colors))
            draw_circle(100)
            mandala.right(10)

    # 중심에 가까운 작은 원들
    for i in range(6):
        mandala.penup()
        mandala.goto(0, 0)
        mandala.pendown()
        draw_pattern()
        mandala.right(60)

    # 바깥쪽 큰 원들
    for i in range(12):
        mandala.penup()
        mandala.goto(0, 0)
        mandala.pendown()
        draw_pattern()
        mandala.right(30)

    mandala.hideturtle()
    screen.mainloop()

def draw_turtle():
    screen = turtle.Screen()
    screen.bgcolor("lightblue")

    t = turtle.Turtle()
    t.speed(3)
    t.width(3)

    def draw_circle(color, radius, x, y):
        t.penup()
        t.goto(x, y)
        t.pendown()
        t.color(color)
        t.begin_fill()
        t.circle(radius)
        t.end_fill()

    def draw_rectangle(color, width, height, x, y):
        t.penup()
        t.goto(x, y)
        t.pendown()
        t.color(color)
        t.begin_fill()
        for _ in range(2):
            t.forward(width)
            t.right(90)
            t.forward(height)
            t.right(90)
        t.end_fill()

    # 몸통
    draw_circle("green", 100, 0, -50)

    # 머리
    draw_circle("green", 50, 0, 100)

    # 눈
    draw_circle("white", 15, -20, 160)
    draw_circle("white", 15, 20, 160)
    draw_circle("black", 5, -20, 175)
    draw_circle("black", 5, 20, 175)

    # 입
    t.penup()
    t.goto(-20, 140)
    t.pendown()
    t.right(90)
    t.circle(20, 180)

    # 다리
    draw_rectangle("green", 20, 60, -70, -150)
    draw_rectangle("green", 20, 60, 50, -150)
    draw_rectangle("green", 20, 60, -70, 50)
    draw_rectangle("green", 20, 60, 50, 50)

    # 꼬리
    t.penup()
    t.goto(-30, -150)
    t.pendown()
    t.color("green")
    t.begin_fill()
    t.goto(0, -200)
    t.goto(30, -150)
    t.end_fill()

    t.hideturtle()
    screen.mainloop()

def initialize_turtle():
    '''
    turtle 모듈 초기화
    '''
    try:
        turtle.bye()
    finally:
        # 약간의 지연 시간을 줌
        time.sleep(0.5)

        # turtle 모듈 다시 가져오기
        import turtle as t
        t.Screen().clear()
        time.sleep(0.5)

def main():
    screen = turtle.Screen()
    screen.bgcolor("lightblue")

    t = turtle.Turtle()
    t.speed(3)
    t.width(3)

    draw_turtle(t)

    t.hideturtle()
    screen.mainloop()

if __name__ == "__main__":
    # initialize_turtle()
    main()
