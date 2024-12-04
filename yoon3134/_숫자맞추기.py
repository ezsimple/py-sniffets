import random

MIN=1 # 최소값
MAX=1000 # 최대값
COUNT=5 # 횟수

print("*숫자 맞추기 게임*")
print(f"기회는 5번, {MIN} ~ {MAX} 까지")

comHand=random.randint(MIN, MAX)
# 숫자

rightAnswer = False # 정답이 아님

for i in range(COUNT) :

  try:
    myHand=int(input(f"{i+1}번째 기회, 숫자를 맞추세요 ==>")) # 문자를 숫자로 변환

    if myHand > MAX:
      print(f"{MAX} 이하의 숫자를 입력하세요.")
      continue

    if myHand < MIN:
      print(f"{MIN} 이상의 숫자를 입력하세요.")
      continue

  except ValueError as e: # 문자를 입력한 경우 오류 발생
    print('숫자를 입력하세요.')
    continue # 돌아가세요.

  if myHand==comHand :
    rightAnswer = True
    print("정답! *^ ^* ")
    break # 정답을 맞추면, for 문장을 벗어나세요.
    
  elif comHand < myHand :
    print("down")
    
  else: # comHand > myHand
    print("up")


if not rightAnswer:
  print(f"실패! 정답은 {comHand} 입니다.")