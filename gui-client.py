from tkinter import *
from tkinter.messagebox import showinfo, showerror
import datetime
from socket import socket, AF_INET, SOCK_STREAM
import re
import time
from DB import DataBase

labelfont = ('times', 25, 'bold')

class login(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.geometry("480x200")
        self.title("Login")
        self.config(bg="#3a4860")
        me = StringVar()
        mp = StringVar()
        serverPort = 8081
        clientServer = socket(AF_INET, SOCK_STREAM)
        clientServer.connect(('localhost', serverPort))
        self.clientServer = clientServer
        Label(self, text="Mail Service", bg='#3a4860', fg='#ffffff',font=labelfont).grid(
            row=1, column=1, sticky=W+E+N+S)
        Label(self, text="Account: ", bg='#3a4860', fg='#ffffff').grid(
            row=2, column=0, sticky=W+E+N+S)
        self.my_email = Entry(self, textvariable=me, width=50)
        self.my_email.grid(row=2, column=1)

        Label(self, text="Password: ", bg='#3a4860', fg='#ffffff').grid(
            row=4, column=0, sticky=W+E+N+S)
        self.my_pass = Entry(self, textvariable=mp, width=50, show="*")
        self.my_pass.grid(row=4, column=1)

        self.email_button = Button(
            self, text="Enter", command=self.login_mail, bg="#576884", fg="#74eaf7")
        self.email_button.grid(row=6, column=1, sticky=W+E+N+S, padx=5, pady=5)

        exit = Button(self, text="Exit", command=self.quit,
                      bg="#576884", fg="#ef3e4a")
        exit.grid(row=7, column=1, sticky=W+E+N+S, padx=5, pady=5)

    def recive_command(self, clientServer):
        recive_data = ""
        while True:
            data = clientServer.recv(1024).decode()
            recive_data = recive_data + data
            if("\r\n" in recive_data):
                break
        return recive_data

    def login_mail(self):
        check_user = False
        check_pass = False
        account = self.my_email.get()
        #account = "mailto@gmail.com"
        self.password = self.my_pass.get()
        #self.password = "123"
        data = self.clientServer.recv(1024).decode()
        print("S: " + data)
        self.clientServer.send(str.encode("user " + account + "\r\n"))
        print("C: user " + account)
        data = self.recive_command(self.clientServer)
        if ("+OK" in data):
            check_user = True
        print("S: " + data)
        if(check_user):
            self.clientServer.send(str.encode(
                "pass " + self.password + "\r\n"))
            data = self.recive_command(self.clientServer)
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
        self.geometry("480x200")
        self.config(bg="#3a4860")
        Label(self, text="Mail Service", bg='#3a4860', fg='#ffffff',font=labelfont).grid(
            row=0, column=1, sticky=W+E+N+S)
        show_inbox = Button(self, text="Inbox",
                            command=self.show_inbox_window,
                            bg="#576884", fg="#74eaf7", width=53)
        show_inbox.grid(row=1, column=0, columnspan=2, rowspan=2,
                        sticky=W+E+N+S, padx=5, pady=5)

        send_mail = Button(self, text="Send Mail",
                           command=self.send_mail_window,
                           bg="#576884", fg="#74eaf7", width=53)
        send_mail.grid(row=4, column=0, columnspan=2, rowspan=2,
                       padx=5, pady=5)
        exit_button = Button(self, text="Exit",
                             command=self.quit,
                             bg="#576884", fg="#ef3e4a", width=53)
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
        self.config(bg="#3a4860")
        self.clientServer = clientServer
        self.account = account
        self.database = DataBase()
        exit_button = Button(self, text="Exit",
                             command=self.quit,
                             bg="black", fg="red")
        exit_button.grid(row=8, column=1, columnspan=2, rowspan=2,
                         padx=5, pady=5)
        message_content = self.transaction_phase()
        print("Transaction finished", message_content)
        for i, mail in enumerate(message_content):
            Label(self, text=mail['Data'], fg="#ffffff", bg="#576884").grid(
                row=20 + i*2, column=1, columnspan=2, rowspan=2,
                padx=5, pady=5, sticky=W+E+N+S)

    def recive_command(self):
        recive_data = ""
        while True:
            data = self.clientServer.recv(1024).decode()
            recive_data = recive_data + data
            if("\r\n" in recive_data):
                break
        return recive_data

    def transaction_phase(self):
        self.clientServer.send("LIST\r\n".encode())
        recived_string = ""

        print("C: " + "list")
        recive_data = self.recive_command()
        recived_string += recive_data
        print("S: " + recive_data)
        message = []
        message.append(recive_data)
        while(True):
            print("S: " + recive_data)
            recive_data = self.recive_command()
            recived_string += recive_data
            print(recived_string)
            if(".\r\n" in recived_string):
                break
            message.append(recive_data)
        print(message)
        message_contents = []
        for i in range(len(message)-1):
            retr = "RETR "
            self.clientServer.send(str(retr + str(i+1) + "\r\n").encode())
            time.sleep(0.2)
            # Recive from
            recive_from = self.recive_command()
            #print("Recive" + recive_from)
            recive_data = self.recive_command()
            #print("S: ... data ...")
            #self.clientServer.send(str("dele " + str(i + 1)).encode())
            time.sleep(0.2)
            #self.database.insert_user_mail(self.account, mail)
            message_contents.append(
                dict(From=recive_from))
        return message_contents


class newEmail(Tk):
    def __init__(self, email_from):
        Tk.__init__(self)
        self.resizable(0, 0)
        self.title("New Email")
        self.geometry("480x200")
        self.config(bg="#3a4860")
        self.mailFrom = email_from
        et = StringVar()
        es = StringVar()
        Label(self, text="From: %s" % self.mailFrom,
              bg='#3a4860', fg='#ffffff').grid(row=0, column=0,)

        Label(self, text="To:", 
            bg='#3a4860', fg='#ffffff').grid(row=1, column=0, sticky=W)
        self.email_to = Entry(self, textvariable=et, width=40)
        self.email_to.grid(row=1, column=1, sticky=E)

        Label(self, text="Subject:", 
            bg='#3a4860', fg='#ffffff').grid(row=2, column=0, sticky=W)
        self.email_subject = Entry(self, textvariable=es, width=40)
        self.email_subject.grid(row=2, column=1, sticky=E)

        Label(self, text="Message:",
         bg='#3a4860', fg='#ffffff').grid(row=3, column=0, sticky=W)
        self.email_msg = Text(self, width=40, height=5)
        self.email_msg.grid(row=3, column=1, sticky=E)

        self.email_button = Button(
            self, text="Send", command=self.sendEmail, bg="#576884", fg="#74eaf7")
        self.email_button.grid(row=4, column=1, sticky=NSEW)

        exit = Button(self, text="Back", command=self.quit,
                      bg="#576884", fg="#74eaf7")
        exit.grid(row=4, column=0, sticky=NSEW)

    def recive_command(self, clientServer):
        recive_data = ""
        while True:
            data = clientServer.recv(1024).decode()
            recive_data = recive_data + data
            if("\r\n" in recive_data):
                break
        return recive_data

    def sendEmail(self):
        now = datetime.datetime.now()
        # self.mailFrom = self.email_from.get()
        self.to = self.email_to.get()
        self.subject = self.email_subject.get()
        self.msg = self.email_msg.get("1.0", END)
        #self.mailFrom = "mailfrom@gmail.com"
        self.mailFrom = "mailfrom@gmail.com"
        self.to = "mailto@santiago.com"
        self.subject = "SUBJECT!"

        regexFrom = re.compile(r"(\w+)(@)(\w+)(\.)(\w+)")
        regexTo = re.compile(r"(\w+)(@)(\w+)(\.)(\w+)+")
        print(self.mailFrom)
        if (re.search(regexFrom, self.mailFrom)):
            if(re.search(regexTo, self.to)):
                serverPort = 8080
                clientServer = socket(AF_INET, SOCK_STREAM)
                clientServer.connect(('localhost', serverPort))
                # Recive 220..
                print("S: " + self.recive_command(clientServer))
                # Send HELO
                clientServer.send(str.encode("HELO rcastro.com\r\n"))
                print("C: HELO rcastro.com")
                # REcive 250..
                print("S: " + self.recive_command(clientServer))
                # Send MAIL FROM
                clientServer.send(str.encode(
                    "MAIL FROM: <" + self.mailFrom + ">\r\n"))
                print("C: " + ("MAIL FROM: <" + self.mailFrom + ">\r\n"))
                # Recive 250 ... sender ok
                print("S: " + self.recive_command(clientServer))
                # send RCPT TO
                clientServer.send(str.encode("RCPT TO: <" + self.to + ">\r\n"))
                print("C: RCPT TO: <" + self.to + ">")
                # Recive 250 ... recipent ok
                print("S: " + self.recive_command(clientServer))
                # Send DATA
                clientServer.send(str.encode("DATA\r\n"))
                print("C: DATA")
                # Recive  354 enter mail ...
                print("S: " + self.recive_command(clientServer))
                clientServer.send(str.encode(self.subject + "\r\n"))
                print("C: " + self.subject)
                clientServer.send(str.encode('\n'))
                print("C: " + '\n')
                clientServer.send(str.encode(self.msg + "\r\n"))
                print("C: " + self.msg)
                clientServer.send(str.encode(".\r\n"))
                print("C: " + ".\n")
                # Recive 250 message accepted
                print("S: " + self.recive_command(clientServer))
                # Send quit
                clientServer.send(str.encode("QUIT\r\n"))
                print("C: QUIT")
                # Recive 221 closing connection ...
                print("S: " + self.recive_command(clientServer))

                clientServer.close()
            else:
                showerror("Error", "Mail to is not valid")
        else:
            showerror("Error", "Mail from is not valid")


L = login()
L.mainloop()