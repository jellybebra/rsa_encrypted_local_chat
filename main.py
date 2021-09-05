import time
import threading
from chat.client import Client
from chat.server import Server
from chat.modules.network_scanner import Network
from chat.modules.constants import Style

cl = Client()

ip = input(f'Enter the IP address (or press Enter): {Style.GREEN}')
print(f'{Style.WHITE}', end='')

if ip == '':
    hosts = Network().scan()

    if cl.connect(hosts):
        cl.start()

    else:
        s = Server()
        server = threading.Thread(target=s.start)
        server.start()

        time.sleep(1)
        cl.connect(hosts)
        client = threading.Thread(target=cl.start)
        client.start()

else:
    hosts = [ip]
    if cl.connect(hosts):
        cl.start()
