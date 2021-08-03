import socket
import threading

"""

TO-DO:
1. Возможность отправлять клиенту сообщения.

"""


class Server(object):
    def __init__(self):
        self.__HEADER = 64
        self.__PORT = 5050
        self.__SERVER = socket.gethostbyname(socket.gethostname())
        self.__ADDRESS = (self.__SERVER, self.__PORT)
        self.__FORMAT = 'utf-8'
        self.__DISCONNECT_MSG = "!DISCONNECT"
        self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server.bind(self.__ADDRESS)

    def __handle_client__(self, conn, addr):
        print(f"[NEW CONNECTION] {addr} connected.")

        connected = True
        while connected:
            msg_length = conn.recv(self.__HEADER).decode(self.__FORMAT)
            if msg_length:
                msg_length = int(msg_length)
                msg = conn.recv(msg_length).decode(self.__FORMAT)
                if msg == self.__DISCONNECT_MSG:
                    connected = False
                print(f"[{addr[0]}] {msg}")
        conn.close()
        # print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

    def start(self):
        self.__server.listen()
        print(f"[LISTENING] Server started. Server is listening on {self.__SERVER}")
        while True:
            conn, addr = self.__server.accept()
            thread = threading.Thread(target=self.__handle_client__, args=(conn, addr))
            thread.start()


if __name__ == '__main__':
    s = Server()
    s.start()
