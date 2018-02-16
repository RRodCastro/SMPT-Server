from pymongo import MongoClient
import pprint

class DataBase:
    def __init__(self):
        self.client = MongoClient()
        self.db = self.client.todos
    def fetch_Mail(self, user):
        print(self.db.bandeja_entrada.find() )
        correos = self.db.bandeja_entrada.find({"To": user})
        for i in correos:
            a = i['From']
            b = i['Subject']
            c = i['Data']
            lista.append(i)
        print(") " + a + " | " + b + " | " + c)
    def save_Mail(self, email_from, email_to, email_sub, email_data):
        self.db.bandeja_entrada.insert({
            "From": email_from, "To": email_to, "Subject": email_sub, "Data": email_data})
        return True


# a = fetch_Mail(user)


'''
q = "Khaliman"
w = "Hugo"
e = "sss"
r = "ok"

save_Mail(q, w, e, r)
'''
#db = DataBase()
#db.fetch_Mail('mailfrom@gmail.com')
#db.save_Mail('testfrom', 'testo', 'testsub', 'email_data')