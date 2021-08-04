import socket
import threading
import os


def cls():
    """
    Clears the screen.
    """
    os.system('cls' if os.name == 'nt' else 'clear')


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
        self.__server.settimeout(None)  # testing
        socket.setdefaulttimeout(None)  # testing

    def __handle_client__(self, conn, addr):
        print(f"\n[NEW CONNECTION] {addr} connected.\n")

        connected = True
        while connected:
            msg_length = conn.recv(self.__HEADER).decode(self.__FORMAT)
            if msg_length:
                msg_length = int(msg_length)
                msg = conn.recv(msg_length).decode(self.__FORMAT)

                if msg == self.__DISCONNECT_MSG:
                    print(f"\n[CONNECTIONS] ({addr[0]}) disconnected.\n")
                    connected = False
                else:
                    print(f"[{addr[0]}] {msg}")
                    conn.send("[SERVER] Message received.".encode(self.__FORMAT))

        conn.close()

    def start(self):
        self.__server.listen()
        cls()
        print(f"[LISTENING] Server started. Server is listening on {self.__SERVER}")

        while True:  # ловим все новые подключения
            conn, addr = self.__server.accept()
            thread = threading.Thread(target=self.__handle_client__, args=(conn, addr))
            thread.start()

    # def message(self):
    #
    #
    # def chat(self):
    #     while True:
    #         mess = input('>>> ')
    #         self.message(mess)


if __name__ == '__main__':
    s = Server()
    s.start()
