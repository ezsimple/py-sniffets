'''

numlist = [10, 20, 30, 40]
print("numlist[-1]은 ", numlist[-1], "numlist[-2]은 ", numlist[-2])

#[-4, -3, -2, -1] 뒤에서부터 시작



mydict = {1:'a', 2:'b', 3:'c'}
print(mydict)


mydict = {'a':1, 'b':2, 'c':3 }
print(mydict)




empdict = {'사번':1000, '이름':'홍길동', '부서':'케이팝'}
print(empdict)

empdict['연락처'] = '010-1111-2222' #추가 


empdict['부서'] = '한빛 아카데미' #변경



del(empdict['부서'])



print(empdict.keys())
print(list(empdict.keys()))


print(empdict.values())

print(empdict.items())



print('이름'in empdict.keys())



empdict = {'사번':1000, '이름':'홍길동', '부서':'케이팝'}


for key in empdict.keys() :
  print(key, empdict[key])

# ====


for key in ['사번', '이름', '부서'] :
  print(key, empdict[key])




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





























    



































