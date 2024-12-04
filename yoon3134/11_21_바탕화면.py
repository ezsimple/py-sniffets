# %%

 #이미지와 같은 폴더로 저장


from tkinter import *
window = Tk()

photo = PhotoImage(file = "Dog.gif")
label1 = Label(window, image = photo)


label1.pack()

window.mainloop()
