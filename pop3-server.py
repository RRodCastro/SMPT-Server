from socket import socket, AF_INET, SOCK_STREAM
from DB import DataBase
import re
import time


class POP3Server:
    def __init__(self, server_socket):
        self.socket = server_socket
        self.database = DataBase()

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

    def authorization_phase(self):
        self.socket.send("+OK POP3 server ready\n".encode())
        print("S: +OK POP3 server ready")
        regex_user = re.compile(r"user (\w+)")
        match = self.process_command(regex_user)
        if(match):
            self.user = match.group(1)
            user = self.database.fetchUser(self.user)
            if (user):
                self.socket.send("+OK".encode())
                print("C: +OK")
                regex_password = re.compile(r"pass (\w+)")
                match = self.process_command(regex_password)
                if(match):
                    self.password = match.group(1)
                    user_and_password = self.database.fetch_user_password(
                        self.user, self.password)
                    if (user_and_password):
                        self.socket.send(
                            "+OK user successfully logged on".encode())
                        print("+OK user successfully logged on")
                        return True
                    else:
                        self.socket.send("-Error".encode())
                        return False
                else:
                    return False
            else:
                self.socket.send("-Error".encode())
                return False
        else:
            return False

    def retr_message(self, message_list):
        for i in enumerate(message_list):
            regex_retr = re.compile(r"retr (\d+)")
            match = self.process_command(regex_retr)
            if (match):
                index = (message_list[int(match.group(1))])
                self.socket.send(index['From'].encode())
                time.sleep(0.2)
                self.socket.send(index['Data'].encode())
                self.socket.send(".".encode())

    def transaction_phase(self):
        regex_list = re.compile(r"list")
        match = self.process_command(regex_list)
        if(match):
            message_list = (self.database.fetch_Mail("mailto@gmail.com"))
            print(message_list)
            for i, mail in enumerate(message_list):
                self.socket.send(
                    str(str(i) + " " + str(len((mail['Data'].encode())))).encode())
                print("S: " + str(str(i) + " " +
                                  str(len((mail['Data'].encode())))))
                time.sleep(0.1)
            self.socket.send(".".encode())
            self.retr_message(message_list)
            # C: dele 1
            # regex = ret #
            #....len
            # C: quit

    def handle_clients(self, serverSocket):
        while(True):
            try:
                print("Waiting clients...")
                connectionSocket, addr = serverSocket.accept()
                self.socket = connectionSocket
                self.transaction_phase()
                self.socket.close()
                break
            except KeyboardInterrupt:
                self.socket.close()
                break


serverPort = 2430
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('localhost', serverPort))
serverSocket.listen(5)
server = POP3Server(serverSocket)
server.handle_clients(serverSocket)
