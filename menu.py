import re
from tkinter import *
# import pymongo
# client = pymongo.MongoClient()
# db = client.




def verCorreo(correo):
    p = re.compile('gmail|hotmail|yahoo|uvg')
    a = p.search(correo)
    if a:
        print('correo valido')
        return True
    else:
        print('correo invalido')
        return False


class Login(Tk):
    def __init__(self, master=None):
        Tk.__init__(self)
        self.title("Simple Login")
        self.config(bg="grey")

        user = StringVar()

        Label(self, text="User: ").grid(row=2, column=0, sticky=W)
        self.profile = Entry(self, textvariable=user, width=50)
        self.profile.grid(row=3, column=0, sticky=W)

        self.login_button = Button(
            self, text="Log in", command=self.enter, bg="green")
        self.login_button.grid(row=5, column=0)
        self.exit_button = Button(
            self, text="Exit", command=self.quit, bg="red")
        self.exit_button.grid(row=6, column=0)

    def enter(self):
        self.user = self.profile.get()
        print("user: " + self.user)

        correo = self.user + "@lostukus.com"

        print ("correo: " + correo)


class Otro(Tk):
    def __init__(self, master=None):
        Tk.__init__(self)
        self.title("Simple Login")
        self.config(bg="red")

        user = StringVar()

        Label(self, text="User: ").grid(row=2, column=0, sticky=W)
        self.profile = Entry(self, textvariable=user, width=50)
        self.profile.grid(row=3, column=0, sticky=W)

        self.login_button = Button(
            self, text="Log in", command=self.enter, bg="green")
        self.login_button.grid(row=5, column=0)
        self.exit_button = Button(
            self, text="Exit", command=self.quit, bg="red")
        self.exit_button.grid(row=6, column=0)

    def enter(self):
        self.user = self.profile.get()
        print("user: " + self.user)

        correo = self.user + "@lostukus.com"

        print ("correo: " + correo)


app = Login()
app.mainloop()

app = Otro()
app.mainloop()
