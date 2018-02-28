from socket import socket, AF_INET, SOCK_STREAM
from DB import DataBase
import re
import time


class POP3Server:
    def __init__(self, server_socket):
        self.socket = server_socket
        self.database = DataBase()
        self.logged_in = False

    def process_command(self, regex):
        recive_data = ""
        while True:
            data = self.socket.recv(1024).decode()
            print(data)
            recive_data = recive_data + data
            if("\r\n" in recive_data):
                break
        print("C: " + recive_data)
        match = re.search(regex, recive_data.split("\r\n")[0])
        if (match):
            return match
        else:
            send_data = ("-ERR\r\n")
            print("S: " + send_data)
            self.socket.send(str.encode(send_data))
            return False

    def authorization_phase(self):
        self.socket.send("+OK POP3 server ready\r\n".encode())
        print("S: +OK POP3 server ready")
        regex_user = re.compile(r"user (.+)")
        match = self.process_command(regex_user)
        if(match):
            self.user = match.group(1)
            user = self.database.fetchUser(self.user)
            while(not user):
                self.socket.send("-ERR\r\n".encode())
                regex_user = re.compile(r"user (.+)")
                match = self.process_command(regex_user)
                if(match):
                    self.user = match.group(1)
                    user = self.database.fetchUser(self.user)
        if (user):
            self.socket.send("+OK\r\n".encode())
            print("C: +OK")
            regex_password = re.compile(r"pass (\w+)")
            match = self.process_command(regex_password)
            if(match):
                self.password = match.group(1)
                user_and_password = self.database.fetch_user_password(
                    self.user, self.password)
                while(not user_and_password):
                    self.socket.send("-ERR\r\n".encode())
                    regex_password = re.compile(r"pass (\w+)")
                    match = self.process_command(regex_password)
                    if(match):
                        self.password = match.group(1)
                        user_and_password = self.database.fetch_user_password(
                            self.user, self.password)
        if (user_and_password):
            self.socket.send(
                "+OK user successfully logged on\r\n".encode())
            print("+OK user successfully logged on")
            self.logged_in = True
            return True
        else:
            return False

    def recive_command(self):
        recive_data = ""
        while True:
            data = self.socket.recv(1024).decode()
            recive_data = recive_data + data
            if("\r\n" in recive_data):
                break
        return recive_data

    def retr_message(self, message_list):
        for i in enumerate(message_list):
            regex_retr = re.compile(r"retr (\d+)")
            match = self.process_command(regex_retr)
            if (match):
                index = (message_list[int(match.group(1))-1])
                self.socket.send(str(index['From'] + "\r\n").encode())
                time.sleep(0.2)
                self.socket.send(str(index['Data'] + "\r\n").encode())
                self.socket.send(".\r\n".encode())
                print("S: .")
                time.sleep(0.2)

    def transaction_phase(self):
        regex_list = re.compile(r"list")
        match = self.process_command(regex_list)
        if(match):
            message_list = (self.database.fetch_Mail("mailto@gmail.com"))
            for i, mail in enumerate(message_list):
                self.socket.send(
                    str(str(i+1) + " " + str(len((mail['Data'].encode()))) + "\r\n").encode())
                print("S: " + str(str(i) + " " +
                                  str(len((mail['Data'].encode())))))
                time.sleep(0.1)
            self.socket.send(".\r\n".encode())
            print("S: .")
            self.retr_message(message_list)
            # C: dele 1

    def quit_phase(self):
        regex_list = re.compile(r"quit")
        match = self.process_command(regex_list)
        if(match):
            self.socket.send("+OK POP3 server signing off\r\n".encode())

    def handle_clients(self, serverSocket):
        while(True):
            try:
                print("Waiting clients...")
                connectionSocket, addr = serverSocket.accept()
                if (not self.logged_in):
                    self.socket = connectionSocket
                self.authorization_phase()
                self.transaction_phase()
                self.quit_phase()
                self.socket.close()
            except KeyboardInterrupt:
                self.socket.close()
                break


serverPort = 8081
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('127.0.0.1', serverPort))
serverSocket.listen(5)
server = POP3Server(serverSocket)
server.handle_clients(serverSocket)
