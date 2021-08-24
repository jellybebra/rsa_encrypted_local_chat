from modules.client import Client
from modules.server import Server
import threading

cl = Client()

if cl.connect():
    cl.start()

else:
    s = Server()
    server = threading.Thread(target=s.start)
    server.start()

    cl.connect()
    client = threading.Thread(target=cl.start)
    client.start()
