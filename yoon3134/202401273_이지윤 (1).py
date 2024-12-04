'''
숫자맞추기 게임 입니다.
기회는 5번, 1~45 까지 숫자에서 고르세요. ^^
'''

import random

print("*숫자 맞추기 게임*")
print("기회는 5번, 1~45 까지")

comHand=random.randint(1,45)


for i in range(5) :

  myHand=int(input("숫자를 맞추세요 ==>"))            

  if myHand==comHand :
    print("정답! *^ ^* ")
    break
    
  elif comHand < myHand :
    print("down")
     
  else :
    print("up")
    
  
 
