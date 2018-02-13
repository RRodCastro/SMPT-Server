from pymongo import *
import pprint

client = MongoClient()
lista = []
user = input("nombre de usuario: ")
db = client.todos
# db.bandeja_entrada.insert({"From": "gg", "Subject": "nada", "To": "Test"})
# db.bandeja_entrada.insert({"From": "gg", "Subject": "ok", "To": "Test"})


def fetch_Mail(user):
    correos = db.bandeja_entrada.find({"To": user})
    for i in correos:
        a = i['From']
        b = i['Subject']
        c = i['Data']
        # lista.append(i)
        print(") " + a + " | " + b + " | " + c)

    # pprint.pprint(lista)
    # return lista


# a = fetch_Mail(user)


def save_Mail(vFrom, vTo, vSub, vData):
    db.bandeja_entrada.insert({
        "From": vFrom, "To": vTo, "Subject": vSub, "Data": vData})
    print("exito")


def show_Mail(mailList):
    for i in range(len(mailList)):
        #a.append(i[0] + i[1])
        print("hola: " + str(a[1]))


'''
q = "Khaliman"
w = "Hugo"
e = "sss"
r = "ok"

save_Mail(q, w, e, r)
'''

a = fetch_Mail(user)
# pprint.pprint(a)
# show_Mail(a)
