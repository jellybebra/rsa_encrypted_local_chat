import socket
import threading
import os


def cls():
    """
    Clears the console.
    """
    os.system('cls' if os.name == 'nt' else 'clear')


class Server(object):
    def __init__(self):
        self.__PORT = 5050
        self.__BPM = 2048  # bits per message
        self.__ACTIVE_CLIENTS = []
        self.__FORMAT = 'utf-8'
        self.__DISCONNECT_MSG = "!DISCONNECT"

        server_ip = socket.gethostbyname(socket.gethostname())
        self.__ADDRESS = (server_ip, self.__PORT)
        self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server.bind(self.__ADDRESS)

    def __handle_client__(self, conn, addr):
        print(f"\n[NEW CONNECTION] {addr} connected.\n")

        def repost_to_others(msg):  # TESTING
            message = msg.encode(self.__FORMAT)

            for client in self.__ACTIVE_CLIENTS:
                client[0].send(message)

                # получение подтверждения получения сообщения
                print(client[0].recv(self.__BPM).decode(self.__FORMAT))  # нужно переделать: HEADER и т.п. ...

        connected = True
        while connected:
            msg = conn.recv(self.__BPM).decode(self.__FORMAT)
            if len(msg):
                if msg == self.__DISCONNECT_MSG:
                    self.__ACTIVE_CLIENTS.remove((conn, addr))
                    print(f"\n[CONNECTIONS] ({addr[0]}) disconnected.\n")
                    connected = False
                else:
                    message = f"[{addr[0]}] {msg}"
                    repost_to_others(message)
                    print(message)
                    conn.send("[SERVER] Message received.".encode(self.__FORMAT))

        conn.close()

    # def chat(self): ################################# added from the CLIENT
    #     while True:
    #         mess = input('>>> ')
    #         self.message(mess)

    def start(self):
        self.__server.listen()
        cls()
        print(f"[LISTENING] Server started. Server is listening on {self.__ADDRESS}")

        while True:  # ловим все новые подключения
            conn, addr = self.__server.accept()
            self.__ACTIVE_CLIENTS.append((conn, addr))
            thread = threading.Thread(target=self.__handle_client__, args=(conn, addr))
            thread.start()


if __name__ == '__main__':
    s = Server()
    s.start()
