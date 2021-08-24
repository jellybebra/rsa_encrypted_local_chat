from modules.client import Client
from modules.server import Server
import threading

cl = Client()

ip = input('Enter the IP address if you have one // press Enter: ')
if cl.connect(ip):
    cl.start()

else:
    s = Server()
    server = threading.Thread(target=s.start)
    server.start()

    cl.connect()
    client = threading.Thread(target=cl.start)
    client.start()
