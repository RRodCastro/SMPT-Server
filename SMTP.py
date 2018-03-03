from socket import socket, AF_INET, SOCK_STREAM, gethostname, gethostbyname
import sys
import threading
import re
from multiprocessing import pool
from DB import DataBase
import time
from threading import Thread
from queue import Queue


class Worker(Thread):
    """ Thread executing tasks from a given tasks queue """

    def __init__(self, tasks):
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.start()

    def run(self):
        while True:
            func, args, kargs = self.tasks.get()
            try:
                func(*args, **kargs)
            except Exception as e:
                # An exception happened in this thread
                print(e)
            finally:
                # Mark this task as done, whether an exception happened or not
                self.tasks.task_done()


class ThreadPool:
    """ Pool of threads consuming tasks from a queue """

    def __init__(self, num_threads):
        self.tasks = Queue(num_threads)
        for _ in range(num_threads):
            Worker(self.tasks)

    def add_task(self, func, *args, **kargs):
        """ Add a task to the queue """
        self.tasks.put((func, args, kargs))

    def map(self, func, args_list):
        """ Add a list of tasks to the queue """
        for args in args_list:
            self.add_task(func, args)

    def wait_completion(self):
        """ Wait for completion of all the tasks in the queue """
        self.tasks.join()


class SMTPServer:
    pool = ThreadPool(5)

    def __init__(self):
        self.smtp_port = 8080
        self.domain = "grupo01.com"
        self.host = gethostbyname(gethostname())

    def process_command(self, regex, socket):
        recive_data = ""
        while True:
            data = socket.recv(1024).decode()
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
            socket.send(str.encode(send_data))
            return False

    def process_message(self, socket):
        recive_data = ""
        while True:
            data = socket.recv(1024).decode()
            recive_data = recive_data + data
            if("\r\n" in recive_data):
                break
        return recive_data.split("\r\n")[0]

    def proces_Helo(self, socket):
        socket.send(str.encode("220 " + self.domain + "\r\n"))
        print("S: 220 " + self.domain)
        regex_helo = re.compile(r"HELO (\w+)(\.)(\w+)")
        match = self.process_command(regex_helo, socket)
        if (match):
            send_data = ("250 HELLO " + match.group(1) + "." +
                         match.group(3) + ", pleased to meet you\r\n")
            socket.send(str.encode(send_data))
            print("S: " + send_data)
            return True
        else:
            return False

    def proces_from(self, socket):
        regex_from = re.compile(r"MAIL FROM: <(\w+)(@)(\w+)(\.)(\w+)>")
        match = self.process_command(regex_from, socket)
        if(match):
            send_data = ("250 " + match.group(1) + match.group(2) +
                         match.group(3) + match.group(4) + match.group(5) + " ... sender Ok\r\n")
            socket.send(str.encode(send_data))
            self.mail_from = match.group(
                1) + match.group(2) + match.group(3) + match.group(4) + match.group(5)
            print("S: " + send_data)
            return True
        else:
            return False

    def process_to(self, socket):
        regex_to = re.compile(r"RCPT TO: <(\w+)(@)(\w+)(\.)(\w+)>")
        match = self.process_command(regex_to, socket)
        if(match):
            send_data = ("250 " + match.group(1) + match.group(2) + match.group(3) +
                         match.group(4) + match.group(5) + " ... recipent Ok\r\n")
            socket.send(str.encode(send_data))
            self.mail_to = match.group(
                1) + match.group(2) + match.group(3) + match.group(4) + match.group(5)
            print("S: " + send_data)
            return True
        else:
            return False

    def process_data(self, socket):
        regex_data = re.compile(r"(DATA)")
        match = self.process_command(regex_data, socket)
        if (match):
            send_data = "354 Enter mail, end with “.” on a line by itself\r\n"
            socket.send(str.encode(send_data))
            print("S: " + send_data)
            recive_data = self.process_message(socket)
            message = recive_data
            while(recive_data != '.'):
                recive_data = self.process_message(socket)
                message += recive_data + "\n"
            print("C: " + message)
            send_data = "250 Message accepted for delivery\r\n"
            self.send_data = message
            socket.send(str.encode(send_data))
            print("S: " + send_data)
            return True
        else:
            return False

    def process_quit(self, socket):
        regex_quit = re.compile(r"(QUIT)")
        match = self.process_command(regex_quit, socket)
        if(match):
            send_data = "221 hamburger.edu closing connection\r\n"
            socket.send(str.encode(send_data))
            print("S: " + send_data)
        else:
            False

    def send_and_recive(self, client_socket, client_address):
        if (self.proces_Helo(client_socket)):
            if(self.proces_from(client_socket)):
                if(self.process_to(client_socket)):
                    if(self.process_data(client_socket)):
                        if(self.process_quit(client_socket)):
                            self.handle_mail(client_socket)

    def handle_mail(self, socket):
        domain = self.mail_to.split("@")[1].replace(">", "")
        print(self.send_data)
        if(domain == self.domain):
            database = DataBase()
            database.save_Mail(
                self.mail_from, self.mail_to, self.send_data)
        else:
            print("sending to..." + domain)
            self.send_mail(domain)

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

    def handle_clients(self, serverSocket, task):
        serverSocket.listen(5)
        while (True):
            try:
                client_socket, client_address = serverSocket.accept()
                self.pool.add_task(
                    self.send_and_recive, client_socket, client_address)
            except KeyboardInterrupt:
                client_socket.close()
                break

    def runnable(self):
        serverSocket = socket(AF_INET, SOCK_STREAM)
        serverSocket.bind((self.host, self.smtp_port))
        print("SMTP running on: ", self.host, self.smtp_port)
        server_thread = Thread(target=self.handle_clients,
                               args=(serverSocket, "smtp"))
        server_thread.start()


server = SMTPServer()
server.runnable()
