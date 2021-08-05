import socket
import threading
from datetime import datetime
import sys
import os

if __name__ == '__main__':
    from find_host_ip import Network
else:
    from .find_host_ip import Network


def cls():
    """
    Clears the screen.
    """
    os.system('cls' if os.name == 'nt' else 'clear')


class Client(object):
    def __init__(self):
        self.__PORT = 5050
        self.__BPM = 2048  # bits per message
        self.__FORMAT = 'utf-8'
        self.__DISCONNECT_MSG = "!DISCONNECT"
        self.__CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def message(self, msg):
        message = msg.encode(self.__FORMAT)
        self.__CLIENT.send(message)

        if msg != self.__DISCONNECT_MSG:
            # подтверждение получения сообщения
            answer = self.__CLIENT.recv(self.__BPM).decode(self.__FORMAT)  # нужно переделать: HEADER и т.п. ...
            print(answer)
        else:
            print('[DISCONNECT] Disconnecting.')
            sys.exit()

    def disconnect(self):
        print('[DISCONNECT] Disconnecting.')
        self.message(self.__DISCONNECT_MSG)
        sys.exit()

    def connect(self):
        """

        Пытаемся подключиться.
        Если не подкючились, пытаемся подключиться (но с большим таймаутом при поиске хостов).

        """

        def try_to_connect():
            connection = False

            t1 = datetime.now()

            for host in hosts:
                try:
                    print(f'[CONNECTING] Trying to connect to {host}...')
                    ADDRESS = (host, self.__PORT)
                    self.__CLIENT = socket.create_connection(ADDRESS, timeout=0.5)  # testing
                    connection = True
                    print('[CONNECTING] Success.')
                    break
                except:
                    print(f'[CONNECTING] FAILED.')

            t2 = datetime.now()
            print(f'[CONNECTING] Time: {t2 - t1}')

            return connection

        hosts = Network().network_scanner(tmout=.02)

        connected = try_to_connect()

        if not connected:
            print('[CONNECTING] Failed. Going for a rescan...')
            hosts = Network().network_scanner()
            connected = try_to_connect()

        print(f"[CONNECTING] Connection {'FAILED' if not connected else 'completed'}.")

        return connected

    def chat(self):
        cls()
        print('Please, type "!DISCONNECT" when you\'re done.', flush=True)
        while True:
            mess = input('>>> ')
            self.message(mess)

    def receive(self):  # TESTING
        while True:
            self.__CLIENT.settimeout(None)  # TESTING
            messages = self.__CLIENT.recv(self.__BPM).decode(self.__FORMAT)
            print(messages)

    # def __handle_client__(self, conn, addr):  ################################### added from the SERVER
    #     print(f"\n[NEW CONNECTION] {addr} connected.\n")
    #
    #     connected = True
    #     while connected:
    #         msg_length = conn.recv(self.__HEADER).decode(self.__FORMAT)
    #         if msg_length:
    #             msg_length = int(msg_length)
    #             msg = conn.recv(msg_length).decode(self.__FORMAT)
    #
    #             if msg == self.__DISCONNECT_MSG:
    #                 print(f"\n[CONNECTIONS] ({addr[0]}) disconnected.\n")
    #                 connected = False
    #             else:
    #                 print(f"[{addr[0]}] {msg}")
    #                 conn.send("[SERVER] Message received.".encode(self.__FORMAT))
    #
    #     conn.close()


if __name__ == '__main__':  # вот эта херня творит ошибки
    cl = Client()
    if cl.connect():
        t1 = threading.Thread(target=cl.chat)
        t1.start()

        t2 = threading.Thread(target=cl.receive)
        t2.start()
    else:
        sys.exit()
