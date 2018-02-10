from socket import socket, AF_INET, SOCK_STREAM
import sys
import threading
import re
from multiprocessing import pool


class SMTPServer:
    def __init__(self, server_socket):
        self.socket = server_socket

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
        self.socket.send(str.encode("220 hamburguer.edu"))
        print("S: 220 hamburguer.edu")
        regex_helo = re.compile(r"(HELO) ([a-zA-Z]+)[.]([a-z]+)")
        match = self.process_command(regex_helo)
        if (match):
            send_data = ("250 HELLO " + match.group(2) + "." +
                         match.group(3) + ", pleased to meet you")
            self.socket.send(str.encode(send_data))
            print("S: " + send_data)
            return True
        else:
            return False

    def proces_from(self):
        regex_from = re.compile(r"(MAIL FROM:) <(\w+)(@)(\w+)(\.)(\w+)>")
        match = self.process_command(regex_from)
        if(match):
            send_data = ("250 " + match.group(2) + match.group(3) +
                         match.group(4) + match.group(5) + match.group(6) + " ... sender Ok")
            self.socket.send(str.encode(send_data))
            print("S: " + send_data)
            return True
        else:
            return False

    def process_to(self):
        regex_to = re.compile(r"(RCPT TO:) <(\w+)(@)(\w+)(\.)(\w+)>")
        match = self.process_command(regex_to)
        if(match):
            send_data = ("250 " + match.group(2) + match.group(3) + match.group(4) +
                         match.group(5) + match.group(6) + " ... recipent Ok")
            self.socket.send(str.encode(send_data))
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
    def send_and_recive (self):
        if (self.proces_Helo()):
            if(self.proces_from()):
                if(self.process_to()):
                    if(self.process_data()):
                        if(self.process_quit()):
                            return True

    def handle_clients(self, serverSocket):
        while (True):
            try:
                print("Waiting clients")
                connectionSocket, addr = serverSocket.accept()
                self.socket = connectionSocket
                self.send_and_recive()
            except KeyboardInterrupt:
                self.socket.close()
                break

serverPort = 2408
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('localhost', serverPort))
serverSocket.listen(5)
server = SMTPServer(serverSocket)
server.handle_clients(serverSocket)

