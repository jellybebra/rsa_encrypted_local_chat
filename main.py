from modules.client import Client
from modules.server import Server

cl = Client()
if cl.connect():  # if connected
    cl.chat()
else:  # become a host
    s = Server()
    s.start()



