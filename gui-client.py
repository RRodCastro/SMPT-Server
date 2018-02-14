from tkinter import *
from tkinter.messagebox import showinfo, showerror
import datetime
from socket import socket, AF_INET, SOCK_STREAM
import re


class login(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.resizable(0,0)
        self.title("Login")        
        me = StringVar()
        mp = StringVar()
        Label(self, text="Account: ").grid(row = 0, column = 0, sticky=W)
        self.my_email = Entry(self, textvariable=me, width = 25)
        self.my_email.grid(row = 0, column = 1)
    
        Label(self, text="Password: ").grid(row = 1, column = 0, sticky=W)
        self.my_pass = Entry(self, textvariable=mp, width = 25)
        self.my_pass.grid(row = 1, column = 1)
 
        self.email_button = Button(self, text="Enter", command=self.login_mail, bg="black", fg="green")
        self.email_button.grid(row = 2, column = 1, sticky=NSEW)
 
        exit = Button(self, text="Exit", command=self.quit, bg="black", fg="red")
        exit.grid(row = 2, column = 0, sticky=NSEW)
        
    def login_mail(self):
        account = self.my_email.get()
        self.password = self.my_pass.get()
        #TODO: Validate with account and pass
        newEmail(account)
        self.withdraw()

class newEmail(Tk):
    def __init__(self, email_from):
        Tk.__init__(self)
        self.resizable(0, 0)
        self.title("New Email") 
        self.config(bg="blue")
        self.mailFrom = email_from
        et = StringVar()
        es = StringVar()
        Label(self, text="From: %s" % self.mailFrom, fg="green").grid(row=0, column=0, sticky=NSEW)

        Label(self, text="To:").grid(row=1, column=0, sticky=W)
        self.email_to = Entry(self, textvariable=et, width=25)
        self.email_to.grid(row=1, column=1, sticky=E)

        Label(self, text="Subject:").grid(row=2, column=0, sticky=W)
        self.email_subject = Entry(self, textvariable=es, width=25)
        self.email_subject.grid(row=2, column=1, sticky=E)

        Label(self, text="Message:").grid(row=3, column=0, sticky=W)
        self.email_msg = Text(self, width=25, height=5)
        self.email_msg.grid(row=3, column=1, sticky=E)

        self.email_button = Button(
            self, text="Send", command=self.sendEmail, bg="black", fg="green")
        self.email_button.grid(row=4, column=1, sticky=NSEW)

        exit = Button(self, text="Exit", command=self.quit,
                       bg="black", fg="red")
        exit.grid(row=4, column=0, sticky=NSEW)

    def sendEmail(self):
        now = datetime.datetime.now()
        #self.mailFrom = self.email_from.get()
        self.to = self.email_to.get()
        self.subject = self.email_subject.get()
        self.msg = self.email_msg.get("1.0", END)
        self.mailFrom = "mailfrom@gmail.com"
        self.to = "mailto@gmail.com"
        self.subject = "SUBJECT!"

        regexFrom = re.compile(r"(\w+)(@)(\w+)(\.)(\w+)")
        regexTo = re.compile(r"(\w+)(@)(\w+)(\.)(\w+)+")
        print(self.mailFrom)
        if (re.search(regexFrom, self.mailFrom)):
            if(re.search(regexTo, self.to)):
                serverPort = 2408
                clientServer = socket(AF_INET, SOCK_STREAM)
                clientServer.connect(('localhost', serverPort))

                data = clientServer.recv(1024).decode()
                print("S: " + data)
                clientServer.send(str.encode("HELO rcastro.com"))
                print("C: HELO rcastro.com")

                data = clientServer.recv(1024).decode()
                print("S: " + data)
                clientServer.send(str.encode(
                    "MAIL FROM: <" + self.mailFrom + ">"))
                print("C: " + ("MAIL FROM: <" + self.mailFrom + ">"))

                data = clientServer.recv(1024).decode()
                print("S: " + data)
                clientServer.send(str.encode("RCPT TO: <" + self.to + ">"))
                print("C: RCPT TO: <" + self.to + ">")

                data = clientServer.recv(1024).decode()
                print("S: " + data)
                clientServer.send(str.encode("DATA"))
                print("C: DATA")

                data = clientServer.recv(1024).decode()
                print("S:" + data)
                clientServer.send(str.encode(self.subject))
                clientServer.send(str.encode('\n'))
                clientServer.send(str.encode('\n'))
                clientServer.send(str.encode(self.msg))
                clientServer.send(str.encode(".\n"))
                data = clientServer.recv(1024).decode()
                print("C: " + self.subject + " " + self.msg)
                print("S: " + data)
                clientServer.send(str.encode("QUIT"))
                print("C: QUIT")

                data = clientServer.recv(1024).decode()
                print("S: " + data)

                clientServer.close()
            else:
                showerror("Error", "Mail to is not valid")
        else:
            showerror("Error", "Mail from is not valid")


L = login()
L.mainloop()
