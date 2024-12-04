import random

print("*숫자 맞추기 게임*")
print("기회는 5번, 1~10 까지")

comHand=random.choice(['1','2','3','4','5','6','7','8','9','10'])


for myHand in range(5) :

  myHand=input("숫자를 맞추세요 ==>")            


  if myHand==comHand :
    print("정답! *^ ^* ")
    break
    

  elif comHand <=myHand :
    print("down")
    
     
  elif myHand <=comHand :
    print("up")
    
  
 

