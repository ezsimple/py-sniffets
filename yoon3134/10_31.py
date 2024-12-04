'''

hap=0
num1, num2 = 0,0

while True :

  num1 = int(input("숫자1 ==> "))
  if num1 == 0 :
    break

  num2 = int(input("숫자2 ==> "))

  hap = num1+num2
  print(num1, "+", num2, "=", hap)


print("0을 입력해서 계산을 종료합니다.")




i, hap =0,0

for i in range(1,101,1) :
  if i % 5 == 0 :
    continue

  hap += i


print("1~100의 합계 (4의 배수 제외) : ", hap)



import random

count = 0
dice1, dice2, dice = 0, 0, 0


while True :
  count += 1
  dice1 = random.randint(1, 6)
  dice2 = random.randint(1, 6)
  dice3 = random.randint(1, 6)

  if (dice1 == dice2) and (dice2 == dice3) :
    break

print("3개의 주사위는 모두", dice1, "입니다.")
print("같은 숫자가 나오기까지", count, "번 던졌습니다.")



import random

count = 0
com = 0

print("*숫자 맞추기 게임*")

while True :
  count += 1
  com = random.randint(1, 6)
  my = int(input(" 숫자를 입력하세요 ==> "))

  if (com == my ) :
    print("*정답*")
    break

  else :
    print("다시시도해보세요!")

print("컴퓨터의 숫자는 ", com, "입니다.")
print(count, "번 시도했습니다.")



import turtle
import random

turtle.shape("turtle")
colors = ['red','green', 'magenta', 'blue', 'black']
turtle.penup()
turtle.screensize(300, 300)
turtle.setup(330, 330)

for i  in range(7) :
  for k in range(7) :
    x = i*50 - 150
    y = k*50 -150
    turtle.goto(x, y)
    turtle.color(random.choice(colors))
    turtle.stamp()

turtle.done()

'''

import turtle
import random

from collections import Counter

def getXYAS() :
  x, y, angle, size = 0, 0, 0, 0
  x = random.randint(-250, 250)
  y = random.randint(-250, 250)
  size = random.randint(10, 50)
  return x, y, size


message = "한 자영업자가 “호의가 계속되면 권리인 줄 안다”며 배달기사에게 무료로 제공했던 음료 서비스를 중단하겠다고 선언했다."



colorList = ['red','green','black','magenta', 'orange', 'gray']
tX, tY, txtSize = 0, 0, 0
char_counts = Counter(message)
unique_chars = list(char_counts.keys())
turtle.shape("turtle")
turtle.setup(550, 550)
turtle.screensize(500, 500)
turtle.penup()
turtle.speed(5)

for char in unique_chars :
  count = char_counts[char]
  tX, tY, txtSize = getXYAS()
  color = random.choice(colorList)
  turtle.goto(tX, tY)
  turtle.pencolor(color)
  turtle.write(char, font=('맑은고딕', txtSize * count, 'bold'))

turtle.done()












































