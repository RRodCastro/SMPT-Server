from tkinter import *
from pymongo import *

client = MongoClient()
lista = []
# cambiar la base de datos
# db = client.todos


class Login(Tk):
    def __init__(self, master=None):
        Tk.__init__(self)
        self.title("Simple Login")
        self.config(bg="grey")

        user = StringVar()
        table_top = StringVar()

        table_top.set('')

        Label(self, text="User: ").grid(row=2, column=0, sticky=W)
        self.profile = Entry(self, textvariable=user, width=50)
        self.profile.grid(row=3, column=0, sticky=W)

        self.login_button = Button(
            self, text="Log in", command=self.enter, bg="green")
        self.login_button.grid(row=5, column=0)
        self.exit_button = Button(
            self, text="Exit", command=self.quit, bg="red")
        self.exit_button.grid(row=6, column=0)
        self.mail = Button(self, text="Correos", command=self.count_Mail)
        self.mail.grid(row=7, column=0)
        Label(self, text=table_top).grid(row=8, column=0, sticky=W)

    def enter(self):
        self.user = self.profile.get()
        # print("user: " + self.user)
        print("S: +OK")

    # funcion para buscar mail de la DB
    def fetch_Mail(self):
        table_top = "No. |   From   |   Subject   |   Data    | \n"
        contador = 0
        self.user = self.profile.get()
        correos = db.bandeja_entrada.find({"To": self.user})
        for i in correos:
            contador += 1
            a = i['From']
            b = i['Subject']
            c = i['Data']
            # lista.append(i)
            table_top = table_top + "   " + \
                str(contador) + "| " + a + " | " + b + " | " + c + "\n"
        print (table_top)

    # funcion para contar correos
    def count_Mail(self):
        self.user = self.profile.get()
        no_correos = db.bandeja_entrada.find({"To": self.user}).count()
        print("OK " + self.user + "'s maildrop has " +
              str(no_correos) + " messages")


app = Login()
app.mainloop()
