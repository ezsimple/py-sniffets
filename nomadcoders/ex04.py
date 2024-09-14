# 거북이로 장미 그리기
# %%

import turtle

# 거북이 모양으로 변경
turtle.shape("turtle")

# 삼각형 그리기
for _ in range(3):
    turtle.forward(100)  # 거북이가 100 만큼 앞으로 이동
    turtle.left(120)     # 거북이가 왼쪽으로 120도 회전

# 화면을 클릭하면 종료
turtle.done()