from socket import socket, AF_INET, SOCK_STREAM
import sys
import threading
import re
from multiprocessing import pool
from DB import DataBase


class SMTPServer:
    def __init__(self, server_socket):
        self.socket = server_socket
        self.domain = "gmail.com"

    def process_command(self, regex):
        recive_data = self.socket.recv(1024).decode()
        print("C: " + recive_data)
        match = re.search(regex, recive_data)
        if (match):
            return match
        else:
            send_data = ("ERROR")
            print("S: " + send_data)
            self.socket.send(str.encode(send_data))
            return False

    def proces_Helo(self):
        self.socket.send(str.encode("220 " + self.domain))
        print("S: 220 " + self.domain)
        regex_helo = re.compile(r"HELO (\w+)(\.)(\w+)")
        match = self.process_command(regex_helo)
        if (match):
            send_data = ("250 HELLO " + match.group(1) + "." +
                         match.group(3) + ", pleased to meet you")
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
                         match.group(3) + match.group(4) + match.group(5) + " ... sender Ok")
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
                         match.group(4) + match.group(5) + " ... recipent Ok")
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
            send_data = "354 Enter mail, end with “.” on a line by itself"
            self.socket.send(str.encode(send_data))
            print("S: " + send_data)
            recive_data = self.socket.recv(1024).decode()
            message = recive_data
            while(recive_data != '.\n'):
                recive_data = self.socket.recv(1024).decode()
                message += recive_data
            print("C: " + message)
            send_data = "250 Message accepted for delivery"
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
            send_data = "221 hamburger.edu closing connection"
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

    def send_mail(self, domain):
        serverPort = 2409
        new_socket = socket(AF_INET, SOCK_STREAM)
        # TODO: Search domain in dns
        new_socket.connect(('localhost', serverPort))
        print("Sending mail to domain: " + domain)
        data = new_socket.recv(1024).decode()
        print("S: " + data)
        new_socket.send(str.encode("HELO " + self.domain))
        print("C: HELO " + self.domain)
        data = new_socket.recv(1024).decode()
        print("S: " + data)
        new_socket.send(str.encode(
            "MAIL FROM: <" + self.mail_from + ">"))
        print("C: " + ("MAIL FROM: <" + self.mail_from + ">"))
        data = new_socket.recv(1024).decode()
        print("S: " + data)
        new_socket.send(str.encode("RCPT TO: <" + self.mail_to + ">"))
        print("C: RCPT TO: <" + self.mail_to + ">")
        data = new_socket.recv(1024).decode()
        print("S: " + data)
        new_socket.send(str.encode("DATA"))
        print("C: DATA")
        data = new_socket.recv(1024).decode()
        print("S:" + data)
        message_line = self.send_data.split('\n')
        for i in len(message_line):
            new_socket.send(str.encode(message_line[i]))
        new_socket.send(str.encode(".\n"))
        data = new_socket.recv(1024).decode()
        print("S: " + data)
        new_socket.send(str.encode("QUIT"))
        print("C: QUIT")
        data = new_socket.recv(1024).decode()
        print("S: " + data)
        new_socket.close()

    def handle_clients(self, serverSocket):
        while (True):
            try:
                print("Waiting clients...")
                connectionSocket, addr = serverSocket.accept()
                self.socket = connectionSocket
                self.send_and_recive()
                domain = self.mail_to.split("@")[1].replace(">", "")
                if(domain == self.domain):
                    database = DataBase()
                    database.save_Mail(
                        self.mail_from, self.mail_to, 'sub', self.send_data)
                else:
                    print("sending to..." + domain)
                    # self.send_mail(domain)
                print("parsed message")
                message_line = self.send_data.split('\n')
                print(message_line)
            except KeyboardInterrupt:
                self.socket.close()
                break


serverPort = 2408
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('localhost', serverPort))
serverSocket.listen(5)
server = SMTPServer(serverSocket)
server.handle_clients(serverSocket)
