'''

num1=int(input("나눠지는 수 ==> "))
num2=int(input("나누는 수 ==> "))
q=num1//num2
r=num1%num2
print(num1,'을(를)', num2, '(으)로 나눈 몫은 ', q, '입니다.')
print(num1,'을(를)', num2, '(으)로 나눈 나머지는 ', r, '입니다.')



#   "%.0f"  소수점 이후 표시할 소수 갯수 %옆의 . 이 중요!


num1=int(input("파운드(1d)를 입력하세요 ==> "))

q=num1*0.453592

print(num1,'파운드는(1d)는 ', "%.5f"%q, '킬로그램(kg)입니다.')


num2=int(input("킬로그램(kg)을 입력하세요 ==> "))

r=num2*2.204623

print(num2,'킬로그램(kg)은 ', "%.5f"%r, '파운드는(1d)입니다.')



num=100+200
num2="100"+"200"

print("num=", num)
print("num2=", num2)




num=100+200
num2=int("100")+int("200")

print("num=", num)
print("num2=", num2)



num1,num2,num3=100,200        #변수 1개당 1개의 값이 주어져야함

num1,num2=100

num1=100,200       #됨


print(num1)


total=0

total-=900*10
total-=3500*5

total+=1800*2
total+=4000*4
total+=1500
total+=2000*4
total+=1800*5

print("오늘 총 매출액은", total, "원입니다.")






score=int(input("필기 시험점수를 입력하세요. ==>"))

print(score >= 70)

#  a >= b  a<= b   a == b  a != b    부등호



 


kor=int(input("국어 입력"))
eng=int(input("영어 입력"))
mat=int(input("수학 입력"))

tot=kor+eng+mat
avg=tot/3

print(avg>=70)


if avg>=70  :
  print("합격")

else  :
  print("불합격")





kor=int(input("국어 입력"))
eng=int(input("영어 입력"))
mat=int(input("수학 입력"))

tot=kor+eng+mat
avg=tot/3

print(avg>=70)


if avg>=90  :
  print("수")

elif avg>=80  :
  print("우")

elif avg>=70  :
  print("미")

else :
  print("재시험봐!!!")








print("중간고사")

kor=int(input("국어 입력"))
eng=int(input("영어 입력"))
mat=int(input("수학 입력"))


print("기말고사")

kor2=int(input("국어 입력"))
eng2=int(input("영어 입력"))
mat2=int(input("수학 입력"))



tot1=kor+eng+mat

tot2=kor2+eng2+mat2


mid=tot1/3
fin=tot2/3

avg=(mid+fin)/2

if mid>=70 and fin>=70 and avg>=70 :
  print("합격")

else :
  print("불합격")




'''


python=3
mobile=2
excel=1

A=4.5
A0=4.0
B=3.5

avg=((python*B)+(mobile*A0)+(excel*A))/(python+mobile+excel)


if avg>=3.5 and  (python*B)>=3.0 and  (mobile*A0)>=3.0 and  (excel*A)>=3.0 :
  print("장학금")















