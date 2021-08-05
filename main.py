from modules.client import Client
from modules.server import Server

cl = Client()

# если присоединились
if cl.connect():
    # запускаем отправку/приём сообщений
    cl.start()

# иначе
else:
    # становимся хостом
    s = Server()
    s.start()



