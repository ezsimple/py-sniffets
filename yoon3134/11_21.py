# 시험 출제

'''

tel = {"김진희":"010111", "임보람":"0011", "김예진":"1111"}
while(True) :
  print("1.연락처 추가")
  print("2.연락처 목록")
  print("3.연락처 검색")
  print("4.종료")

  menu = input("메뉴 선택: ")


  if menu == "1" :
    name = input("이름: ")
    phone_number = input("연락처:  ")
    tel[name] = phone_number

  elif menu == "2" :
    print("-----------------------------------")
    print(tel)
    print("-----------------------------------")

  elif menu == "3" :
    name = input("검색할 이름: ")

    if name in tel :                       ##중요
      print(name, ":", tel[name])

    else :
      print("목록에 존재하지 않는 이름입니다.")
    

  else :
    break

print("프로그램을 종료합니다.")


'''
# %%
#책 12장
from tkinter import *

window = Tk()

window.title("윈도창 연습")
window.geometry("500x500")
#window.resizable(width = FALSE, height = FALSE)



label1 = Label(window, text = "COOKBOOK~ python을")
label2 = Label(window, text = "열심히", font = ("궁서체", 30), fg = "blue")
label3 = Label(window, text = "공부 중입니다.", bg = "magenta", width = 20, height = 5, anchor = SE)

label1.pack()
label2.pack()
label3.pack()

window.mainloop()























