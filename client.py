import socket
from find_host_ip_wo_nmap import Network
from datetime import datetime


"""

Проблемы:
1. Если хостов больше, чем один, то слишком долго подключается к неправильному хосту, нужно сделать таймаут 
   в 1 секунду: https://stackoverflow.com/questions/3432102/python-socket-connection-timeout
   
"""


class Client(object):
    def __init__(self):
        self.__HEADER = 64
        self.__PORT = 5050
        self.__FORMAT = 'utf-8'
        self.__DISCONNECT_MSG = "!DISCONNECT"
        self.__CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect_to(self, server):
        """
        Проблема[1]
        """
        ADDRESS = (server, self.__PORT)
        # socket.setdefaulttimeout(10.0)  # doesn't work
        # self.__CLIENT.settimeout(10.0)  # doesn't work
        self.__CLIENT.connect(ADDRESS)
        # self.__CLIENT.settimeout(None)  # doesn't work

    def message(self, msg):
        message = msg.encode(self.__FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode(self.__FORMAT)
        send_length += b' ' * (self.__HEADER - len(send_length))

        self.__CLIENT.send(send_length)
        self.__CLIENT.send(message)
        if msg != self.__DISCONNECT_MSG:
            print(f'[SEND] Sent send_length: {send_length}')
            print(f'[SEND] Sent message: {message}')

    def disconnect(self):
        print('[DISCONNECT] Disconnecting.')
        self.message(self.__DISCONNECT_MSG)

    def connect(self):
        hosts = Network().network_scanner()

        t1 = datetime.now()

        for host in hosts:
            try:
                print(f'[CONNECTING] Trying to connect to {host}...')
                self.connect_to(host)
                print('[CONNECTING] Success.')
                break
            except:
                print(f'[CONNECTING] Failed.')

        t2 = datetime.now()
        print(f"[CONNECTING] Connection completed in: {t2 - t1}")


if __name__ == '__main__':
    cl = Client()
    cl.connect()
    cl.message('Hello!')
    cl.disconnect()
