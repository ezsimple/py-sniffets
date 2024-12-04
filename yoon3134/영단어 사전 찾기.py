'''

dict = {'flower':'꽃', 'tree':'나무', 'boare': '보드', 'apple':'사과', 'key':'열쇠', 'banana':'바나나', 'student':'학생', 'cat':'고양이', 'weather':'날씨', 'rain':'비'}



for i in range(5) :

  word = input("영단어를 입력하세요.==> ")
 
  
  if word in dict.keys() :
    print(word, ":", dict[word])
    

  else :
    print("사전에 없는 단어 입니다.")



'''


dict = {'flower':'꽃', 'tree':'나무', 'boare': '보드', 'apple':'사과', 'key':'열쇠', 'banana':'바나나', 'student':'학생', 'cat':'고양이', 'weather':'날씨', 'rain':'비'}


while True :
  word = input("찾는 단어는? ")


  if word in dict.keys() :
    print(word, ":", dict[word])

  quit = input("계속할까요? (y/n) ")


  if quit == 'n' :
    break
