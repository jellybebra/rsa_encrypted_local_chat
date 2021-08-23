from modules.client import Client
from modules.server import Server
import threading

cl = Client()

# если присоединились
if cl.connect():
    # запускаем отправку/приём сообщений
    cl.start()

# иначе
else:
    # запускаем сервер
    s = Server()
    t1 = threading.Thread(target=s.start)
    t1.start()

    # запускаем клиент
    if cl.connect():
        # запускаем отправку/приём сообщений
        t2 = threading.Thread(target=cl.start)
        t2.start()
