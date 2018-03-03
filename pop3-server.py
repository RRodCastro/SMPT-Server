from socket import socket, AF_INET, SOCK_STREAM, gethostname, gethostbyname
from DB import DataBase
import re
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


class POP3Server:
    pool = ThreadPool(5)

    def __init__(self):
        self.smtp_port = 8085
        self.database = DataBase()
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
            send_data = ("-ERR\r\n")
            print("S: " + send_data)
            socket.send(str.encode(send_data))
            return False

    def authorization_phase(self, socket):
        user_and_password = False
        socket.send("+OK POP3 server ready\r\n".encode())
        print("S: +OK POP3 server ready")
        regex_user = re.compile(r"USER (.+)")
        match = self.process_command(regex_user, socket)
        if(match):
            user_name = match.group(1)
            user = self.database.fetchUser(user_name)
            while(not user):
                socket.send("-ERR\r\n".encode())
                regex_user = re.compile(r"USER (.+)")
                match = self.process_command(regex_user, socket)
                if(match):
                    user_name = match.group(1)
                    user = self.database.fetchUser(user_name)
        if (user):
            socket.send("+OK\r\n".encode())
            print("S: +OK")
            regex_password = re.compile(r"PASS (.+)")
            match = self.process_command(regex_password, socket)
            if(match):
                password = match.group(1)
                user_and_password = self.database.fetch_user_password(
                    user_name, password)
                while(not user_and_password):
                    socket.send("-ERR\r\n".encode())
                    regex_password = re.compile(r"PASS (\w+)")
                    match = self.process_command(regex_password, socket)
                    if(match):
                        password = match.group(1)
                        user_and_password = self.database.fetch_user_password(
                            user_name, password)
        if (user_and_password, socket):
            socket.send(
                "+OK user successfully logged on\r\n".encode())
            print("+OK user successfully logged on")
            return user_name

    def recive_command(self, socket):
        recive_data = ""
        while True:
            data = socket.recv(1024).decode()
            recive_data = recive_data + data
            if("\r\n" in recive_data):
                break
        return recive_data

    def retr_message(self, message_list, socket):
        for i in enumerate(message_list):
            # Recive RETR # of_message
            regex_retr = re.compile(r"RETR (\d+)")
            match = self.process_command(regex_retr, socket)
            if (match):
                index = (message_list[int(match.group(1))-1])
                message = str(index['From'] + "\n\n" +
                              str(index['Data'] + "\r\n"))
                socket.send(message.encode())
                print("S: " + message)
                socket.send(".\r\n".encode())
                print("S: .\r\n")
                # REcive DELE # of_message
                regex_dele = re.compile(r"DELE (\d+)")
                match = self.process_command(regex_dele, socket)
                if(match):
                    print("Deleting messages ... " + str(index))

    def transaction_phase(self, socket, user_name):
        regex_list = re.compile(r"LIST")
        match = self.process_command(regex_list, socket)
        if(match):
            message_list = (self.database.fetch_Mail(user_name))
            # SEND:  +OK n messages size_of_messages
            messages = "+OK " + str(len(message_list)) + \
                " messages " + str(len(message_list) * 7) + "\r\n"
            socket.send(messages.encode())
            print("S: ", messages)
            # SEND LIST of messages (message_number message_size)
            for i, mail in enumerate(message_list):
                socket.send(
                    str(str(i+1) + " " + str(len((mail['Data'].encode()))) + "\r\n").encode())
                print("S: " + str(str(i) + " " +
                                  str(len((mail['Data'].encode())))))
                time.sleep(0)
            socket.send(".\r\n".encode())
            print("S: .\r\n")
            if(len(message_list) > 0):
                self.retr_message(message_list, socket)
                self.quit_phase(socket)
            # nothing to retr
            else:
                self.quit_phase(socket)

    def quit_phase(self, socket):
        regex_list = re.compile(r"QUIT")
        match = self.process_command(regex_list, socket)
        if(match):
            socket.send("+OK POP3 server signing off\r\n".encode())

    def phases(self, socket, socket_address):
        user_name = self.authorization_phase(socket)
        self.transaction_phase(socket, user_name)
        socket.close()
        # Delete mail after connection is closed
        # self.database.delete_mail(user_name)

    def handle_clients(self, serverSocket, task):
        serverSocket.listen(5)
        while(True):
            try:
                client_socket, client_address = serverSocket.accept()
                self.pool.add_task(
                    self.phases, client_socket, client_address)
            except KeyboardInterrupt:
                client_socket.close()
                break

    def runnable(self):
        serverSocket = socket(AF_INET, SOCK_STREAM)
        serverSocket.bind((self.host, self.smtp_port))
        print("POP3 running on: ", self.host, self.smtp_port)
        server_thread = Thread(target=self.handle_clients,
                               args=(serverSocket, "pop3"))
        server_thread.start()


server = POP3Server()
server.runnable()
