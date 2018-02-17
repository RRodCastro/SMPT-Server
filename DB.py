from pymongo import MongoClient
import pprint


class DataBase:
    def __init__(self):
        self.client = MongoClient()
        self.db = self.client.smtp

    def fetch_Mail(self, user):
        correos = self.db.server_mails.find({"To": user}, {"_id": 0})
        for i in correos:
            print(i)
            a = i['From']
            b = i['Subject']
            c = i['Data']

    def save_Mail(self, email_from, email_to, email_sub, email_data):
        self.db.server_mails.insert({
            "From": email_from, "To": email_to, "Subject": email_sub, "Data": email_data})
        return True

#db = DataBase()
# db.fetch_Mail("mailto@gmail.com")
#db.save_Mail('testfrom', 'testo', 'testsub', 'email_data')
