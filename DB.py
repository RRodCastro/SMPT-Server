from pymongo import MongoClient, DESCENDING
import pprint
from bson.objectid import ObjectId


class DataBase:
    def __init__(self):
        self.client = MongoClient()
        self.db = self.client.smtp

    def insertUser(self, user_name, password):
        self.db.users.insert({"user_name": user_name, "password": password})

    def fetchUser(self, user_name):
        user = self.db.users.find_one({"user_name": user_name})
        if(user is None):
            return False
        else:
            return True

    def insert_user_mail(self, account, mail):
        self.db[account].insert({"Data": mail})

    def fetch_user_password(self, user_name, password):
        user_and_pass = self.db.users.find_one(
            {"user_name": user_name, "password": password})
        if(user_and_pass is None):
            return False
        else:
            return True

    def delete_mail(self, to):
        self.db.server_mails.remove({"To": to})

    def fetch_Mail(self, user):
        mails = self.db.server_mails.find({"To": user})
        message_list = []
        for i, mail in enumerate(mails):
            message_list.append(mail)
        return message_list

    def list_mail(self, user):
        correos = self.db.server_mails.find({"To": user})
        message_list = []
        for i, mail in enumerate(correos):
            message_list.append(
                dict(id=mail['_id'], index=i, message_len=len((mail['Data'].encode()))))
        return message_list

    def save_Mail(self, email_from, email_to, email_data):
        self.db.server_mails.insert({
            "From": email_from, "To": email_to, "Data": email_data})
        return True

    def fetch_mail_from_account(self, account):
        mails = self.db[account].find().sort("_id", DESCENDING)
        message_list = []
        for i, mail in enumerate(mails):
            message_list.append(mail)
        return message_list


#db = DataBase()
#db.insert_user_mail("rrgmailcom", "Data data data")
