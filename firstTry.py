from tkinter import *

root = Tk()
root.title("Cuki2Sepidz")
root.iconbitmap("./logo64x64.ico")
root.geometry("500x300")
root.resizable(0, 0)


# login frame
loginFrame = LabelFrame(root, text="ورود", labelanchor='ne', pady=10, padx=10)
usernameLabel = Label(loginFrame, text=":نام کاربری").grid(row=0, column=2, pady=3)
usernameInput = Entry(loginFrame).grid(row=0, column=1, pady=3)
passwordLabel = Label(loginFrame, text=":رمز عبور").grid(row=1, column=2, pady=3)
passwordInput = Entry(loginFrame, show="*").grid(row=1, column=1, pady=3)
loginButton = Button(loginFrame, text="ورود", padx=20).grid(row=2, column=1, pady=10)
emptyLabelToJustify = Label(loginFrame, padx=20).grid(row=0, column=0)
loginFrame.pack()


# status bar frame
statusFrame = Frame(root, bd=2, relief=SUNKEN)
statusLabel = Label(statusFrame, text="سلام", padx=5, pady=1).pack(side=RIGHT)
statusFrame.pack(side=BOTTOM, fill=X)



root.mainloop()
