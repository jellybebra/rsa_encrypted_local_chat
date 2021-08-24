from modules.client import Client
from modules.server import Server
import threading

# запускаем клиент
cl = Client()

# если присоединились
if cl.connect():
    cl.start()

else:
    # запускаем сервер
    s = Server()
    server = threading.Thread(target=s.start)
    server.start()

    # запускаем клиент
    cl.connect()
    client = threading.Thread(target=cl.start)
    client.start()
