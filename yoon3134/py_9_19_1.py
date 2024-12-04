'''

print(100+200)



def number(a=0, b=0):
  print(100+200*a/b)

number(600, 600)



#print(100+200)

a=100
b=200

print(a+b)




#문제) 중간, 기말, 과제, 출석 점수를 4개를 가지고 평균을 출력하시오.
mid=100
fin=100
homew=100
att=100

avg=(mid+fin+homew+att)/4  #avg 연산 순서에 맞춰 계산
all=mid+fin+homew+att



print("학과:", "유니버셜아트디자인학과")
print("학번:", 202401273)
print("이름:", "이지윤")

print("평균=", avg, "총점=", all )



def number(mid, fin, homew, att):
  
  
  all=mid+fin+homew+att
  avg=all/4
  
  print("총점=", all, "평균=", avg)


number(100, 100, 50, 100)



num1=100
num2=200

result1=num1+num2
result2=num1-num2
result3=num1*num2
result4=num1/num2


print(result1, "=", num1, "+", num2)
print(result2, "=", num1, "-", num2)
print(result3, "=", num1, "*", num2)
print(result4, "=", num1, "/", num2)



kor=int(input("국어점수 입력:"))
eng=int(input("영어점수 입력:"))
mat=int(input("수학점수 입력:"))

tot=kor+eng+mat
avg=tot/3
print("김진희 평균=%.2f"%avg)




print("## 택배를 보내기 위한 정보를 입력하세요. ##")
personName=input("받는 사람 : ")
personaddr=input("주소 : ")
weight=int(input("무게(g) :"))

print("** 받는 사람 ==>", personName)
print("** 주소 ==>", personaddr)

print("** 배송비 ==>", weight*5, "원")


'''

num1=int(input("숫자1 ==> "))
num2=int(input("숫자2 ==> "))



result1=num1+num2
result2=num1-num2
result3=num1*num2
result4=num1/num2
result5=num1%num2
result6=num1**num2

print(num1, "+", num2, "=", result1)
print(num1, "-", num2, "=", result2)
print(num1, "*", num2, "=", result3)
print(num1, "/", num2, "=", result4)
print(num1, "%", num2, "=", result5)
print(num1, "**", num2, "=", result6)











