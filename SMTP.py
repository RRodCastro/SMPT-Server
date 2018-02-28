from socket import socket, AF_INET, SOCK_STREAM
import sys
import threading
import re
from multiprocessing import pool
from DB import DataBase
import time


class SMTPServer:
    def __init__(self, server_socket):
        self.socket = server_socket
        self.domain = "gmail.com"

    def process_command(self, regex):
        recive_data = ""
        while True:
            data = self.socket.recv(1024).decode()
            recive_data = recive_data + data
            if("\r\n" in recive_data):
                break
        print("C: " + recive_data)
        match = re.search(regex, recive_data.split("\r\n")[0])
        if (match):
            return match
        else:
            send_data = ("ERROR")
            print("S: " + send_data)
            self.socket.send(str.encode(send_data))
            return False

    def process_message(self):
        recive_data = ""
        while True:
            data = self.socket.recv(1024).decode()
            recive_data = recive_data + data
            if("\r\n" in recive_data):
                break
        return recive_data.split("\r\n")[0]

    def proces_Helo(self):
        self.socket.send(str.encode("220 " + self.domain + "\r\n"))
        print("S: 220 " + self.domain)
        regex_helo = re.compile(r"HELO (\w+)(\.)(\w+)")
        match = self.process_command(regex_helo)
        if (match):
            send_data = ("250 HELLO " + match.group(1) + "." +
                         match.group(3) + ", pleased to meet you\r\n")
            self.socket.send(str.encode(send_data))
            print("S: " + send_data)
            return True
        else:
            return False

    def proces_from(self):
        regex_from = re.compile(r"MAIL FROM: <(\w+)(@)(\w+)(\.)(\w+)>")
        match = self.process_command(regex_from)
        if(match):
            send_data = ("250 " + match.group(1) + match.group(2) +
                         match.group(3) + match.group(4) + match.group(5) + " ... sender Ok\r\n")
            self.socket.send(str.encode(send_data))
            self.mail_from = match.group(
                1) + match.group(2) + match.group(3) + match.group(4) + match.group(5)
            print("S: " + send_data)
            return True
        else:
            return False

    def process_to(self):
        regex_to = re.compile(r"RCPT TO: <(\w+)(@)(\w+)(\.)(\w+)>")
        match = self.process_command(regex_to)
        if(match):
            send_data = ("250 " + match.group(1) + match.group(2) + match.group(3) +
                         match.group(4) + match.group(5) + " ... recipent Ok\r\n")
            self.socket.send(str.encode(send_data))
            self.mail_to = match.group(
                1) + match.group(2) + match.group(3) + match.group(4) + match.group(5)
            print("S: " + send_data)
            return True
        else:
            return False

    def process_data(self):
        regex_data = re.compile(r"(DATA)")
        match = self.process_command(regex_data)
        if (match):
            send_data = "354 Enter mail, end with “.” on a line by itself\r\n"
            self.socket.send(str.encode(send_data))
            print("S: " + send_data)
            recive_data = self.process_message()
            message = recive_data
            while(recive_data != '.'):
                recive_data = self.process_message()
                message += recive_data + "\n"
            print("C: " + message)
            send_data = "250 Message accepted for delivery\r\n"
            self.send_data = message
            self.socket.send(str.encode(send_data))
            print("S: " + send_data)
            return True
        else:
            return False

    def process_quit(self):
        regex_quit = re.compile(r"(QUIT)")
        match = self.process_command(regex_quit)
        if(match):
            send_data = "221 hamburger.edu closing connection\r\n"
            self.socket.send(str.encode(send_data))
            print("S: " + send_data)
        else:
            False

    def send_and_recive(self):
        if (self.proces_Helo()):
            if(self.proces_from()):
                if(self.process_to()):
                    if(self.process_data()):
                        if(self.process_quit()):
                            return True

    def recive_command(self, clientServer):
        recive_data = ""
        while True:
            data = clientServer.recv(1024).decode()
            recive_data = recive_data + data
            if("\r\n" in recive_data):
                break
        return recive_data

    def send_mail(self, domain):
        serverPort = 2409
        clientServer = socket(AF_INET, SOCK_STREAM)
        # TODO: Search domain in dns
        clientServer.connect(('localhost', serverPort))
        print("Sending mail to domain: " + domain)
        # RECIVE 220
        print("S: " + self.recive_command(clientServer))
        # SEND HELO
        clientServer.send(str.encode("HELO " + self.domain + "\r\n"))
        print("C: HELO " + self.domain)
        # RECIVE 250 HELLO
        print("S: " + self.recive_command(clientServer))
        # SEND MAIL FROM
        clientServer.send(str.encode(
            "MAIL FROM: <" + self.mail_from + ">"))
        print("C: " + ("MAIL FROM: <" + self.mail_from + ">\r\n"))
        #  RECIVE 250 ... sender ok
        print("S: " + self.recive_command(clientServer))
        clientServer.send(str.encode("RCPT TO: <" + self.mail_to + ">\r\n"))
        # SEND RCPT TO:
        print("C: RCPT TO: <" + self.mail_to + ">\r\n")
        # RECIVE 250 ... recipent ok
        print("S: " + self.recive_command(clientServer))
        # SEND DATA
        clientServer.send(str.encode("DATA\r\n"))
        print("C: DATA")
        # RECIVE 354 enter mail ...
        print("S: " + self.recive_command(clientServer))
        message_line = self.send_data.split("\n")
        # -2 Remove "." + "\n" from message
        for i in range(len(message_line)-2):
            clientServer.send(str.encode(message_line[i]))
            clientServer.send(str.encode("\r\n"))
            print("send... " + message_line[i])
        clientServer.send(str.encode(".\r\n"))
        # RECIVE 250 message accepted
        print("S: " + self.recive_command(clientServer))
        # SEND QUIT
        clientServer.send(str.encode("QUIT\r\n"))
        print("C: QUIT")
        # RECIVE 221 closing
        print("S: " + self.recive_command(clientServer))
        clientServer.close()

    def handle_clients(self, serverSocket):
        while (True):
            try:
                print("Waiting clients...")
                connectionSocket, addr = serverSocket.accept()
                self.socket = connectionSocket
                self.send_and_recive()
                domain = self.mail_to.split("@")[1].replace(">", "")
                print(self.send_data)
                if(domain == self.domain):
                    database = DataBase()
                    database.save_Mail(
                        self.mail_from, self.mail_to, self.send_data)
                else:
                    print("sending to..." + domain)
                    self.send_mail(domain)
            except KeyboardInterrupt:
                self.socket.close()
                break


serverPort = 8888
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('127.0.0.1', serverPort))
serverSocket.listen(5)
server = SMTPServer(serverSocket)
server.handle_clients(serverSocket)
