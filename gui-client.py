from tkinter import *
from tkinter.messagebox import showinfo, showerror
import datetime
from socket import socket, AF_INET, SOCK_STREAM
import re
import time
from DB import DataBase


class login(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.resizable(0, 0)
        self.title("Login")
        me = StringVar()
        mp = StringVar()
        Label(self, text="Account: ").grid(row=0, column=0, sticky=W)
        self.my_email = Entry(self, textvariable=me, width=25)
        self.my_email.grid(row=0, column=1)

        Label(self, text="Password: ").grid(row=1, column=0, sticky=W)
        self.my_pass = Entry(self, textvariable=mp, width=25)
        self.my_pass.grid(row=1, column=1)

        self.email_button = Button(
            self, text="Enter", command=self.login_mail, bg="black", fg="green")
        self.email_button.grid(row=2, column=1, sticky=NSEW)

        exit = Button(self, text="Exit", command=self.quit,
                      bg="black", fg="red")
        exit.grid(row=2, column=0, sticky=NSEW)

    def login_mail(self):
        check_user = False
        check_pass = False
        account = self.my_email.get()
        #account = "leo@gmail.com"
        self.password = self.my_pass.get()
        #self.password = "leo123"
        serverPort = 2000
        clientServer = socket(AF_INET, SOCK_STREAM)
        clientServer.connect(('192.168.43.17', serverPort))
        self.clientServer = clientServer
        data = self.clientServer.recv(1024).decode()
        print("S: " + data)
        self.clientServer.send(str.encode("user " + account))
        print("C: user " + account)
        data = self.clientServer.recv(1024).decode()
        if ("+OK" in data):
            check_user = True
        print("S: " + data)
        if(check_user):
            self.clientServer.send(str.encode("pass " + self.password))
            data = self.clientServer.recv(1024).decode()
            print("S: " + data)
            if ("+OK" in data):
                check_pass = True
        if (check_pass & check_user):
            menu(self.my_email.get(), self.clientServer)
            self.withdraw()
        else:
            showerror("Error", "User or Password doesnt match")


class menu(Tk):
    def __init__(self, account, clientServer):
        Tk.__init__(self)
        self.account = account
        self.clientServer = clientServer
        self.title("Menu")
        self.config(bg="blue")
        show_inbox = Button(self, text="                 Inbox                  ",
                            command=self.show_inbox_window,
                            bg="black", fg="green")
        show_inbox.grid(row=0, column=0, columnspan=2, rowspan=2,
                        sticky=W+E+N+S, padx=5, pady=5)

        send_mail = Button(self, text="                 Send Mail                  ",
                           command=self.send_mail_window,
                           bg="black", fg="green")
        send_mail.grid(row=4, column=0, columnspan=2, rowspan=2,
                       padx=5, pady=5)
        exit_button = Button(self, text="                 Exit                  ",
                             command=self.quit,
                             bg="black", fg="red")
        exit_button.grid(row=8, column=0, columnspan=2, rowspan=2,
                         padx=5, pady=5)

    def send_mail_window(self):
        newEmail(self.account)
        self.withdraw()

    def show_inbox_window(self):
        inbox(self.account, self.clientServer)
        self.withdraw()


class inbox(Tk):
    def __init__(self, account, clientServer):
        Tk.__init__(self)
        self.title("Inbox")
        self.config(bg="blue")
        self.clientServer = clientServer
        self.account = account
        self.database = DataBase()
        exit_button = Button(self, text="Exit",
                             command=self.quit,
                             bg="black", fg="red")
        exit_button.grid(row=8, column=0, columnspan=2, rowspan=2,
                         padx=5, pady=5)
        message_content = self.transaction_phase()
        print("Transaction finished", message_content)
        for i, mail in enumerate(message_content):
            Label(self, text=mail['Data']).grid(
                row=10+i, column=0, columnspan=2, rowspan=2,
                padx=5, pady=5)

    def transaction_phase(self):
        self.clientServer.send("list".encode())
        print("C: " + "list")
        recive_data = self.clientServer.recv(1024).decode()
        print("S: " + recive_data)
        message = []
        message.append(recive_data)
        while(recive_data != '.'):
            print("S: " + recive_data)
            recive_data = self.clientServer.recv(1024).decode()
            message.append(recive_data)
        print(message[0: len(message)-1])
        message_contents = []
        for i in range(len(message)-1):
            retr = "retr "
            self.clientServer.send((retr + str(i+1)).encode())
            print(retr + str(i+1))
            time.sleep(0.2)
            # Recive from
            recive_from = self.clientServer.recv(1024).decode()
            recive_content = self.clientServer.recv(1024).decode()
            recive_data = self.clientServer.recv(1024).decode()
            print("S: ... data ...")
            self.clientServer.send(str("dele " + str(i + 1)).encode())
            time.sleep(0.2)
            #self.database.insert_user_mail(self.account, mail)
            message_contents.append(
                dict(From=recive_from, Data=recive_content))
        return message_contents


class newEmail(Tk):
    def __init__(self, email_from):
        Tk.__init__(self)
        self.resizable(0, 0)
        self.title("New Email")
        self.config(bg="blue")
        self.mailFrom = email_from
        et = StringVar()
        es = StringVar()
        Label(self, text="From: %s" % self.mailFrom,
              fg="green").grid(row=0, column=0,)

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
        # self.mailFrom = self.email_from.get()
        self.to = self.email_to.get()
        self.subject = self.email_subject.get()
        self.msg = self.email_msg.get("1.0", END)
        self.mailFrom = "mailfrom@gmail.com"
        self.to = "mailto@hotmail.com"
        self.subject = "SUBJECT!"

        regexFrom = re.compile(r"(\w+)(@)(\w+)(\.)(\w+)")
        regexTo = re.compile(r"(\w+)(@)(\w+)(\.)(\w+)+")
        print(self.mailFrom)
        if (re.search(regexFrom, self.mailFrom)):
            if(re.search(regexTo, self.to)):
                serverPort = 2407
                clientServer = socket(AF_INET, SOCK_STREAM)
                clientServer.connect(('192.168.43.17', serverPort))

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
                print("C: " + self.subject)
                clientServer.send(str.encode('\n'))
                print("C: " + '\n')
                clientServer.send(str.encode(self.msg))
                print("C: " + self.msg)
                clientServer.send(str.encode(".\n"))
                print("C: " + ".\n")
                data = clientServer.recv(1024).decode()
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
