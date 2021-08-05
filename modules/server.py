import os
import socket
import threading


def cls():
    """
    Clears the console.
    """
    os.system('cls' if os.name == 'nt' else 'clear')


class Server:
    def __init__(self):
        # создаём полный адрес сервера
        self.__PORT = 5050
        self.__SERVER_IP = socket.gethostbyname(socket.gethostname())
        self.__ADDRESS = (self.__SERVER_IP, self.__PORT)

        # создаём сокет на заданном адресе
        self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server.bind(self.__ADDRESS)

        # некоторые доп. переменные
        self.active_clients = []  # данные всех подключенных на данный момент клиентов
        self.__BPM = 2048  # Bits Per Message - число бит для кодир-я 1 сообщения (взяли максимальное из-за лени)
        self.__FORMAT = 'utf-8'  # кодировка
        self.__DISCONNECT_MSG = '!disconnect'

    def __handle_client__(self, conn, addr):
        # будем обслуживать пользователя, пока он не отключится
        connected = True
        while connected:
            # ждём нового сообщения от пользователя
            incoming_message = conn.recv(self.__BPM).decode(self.__FORMAT)

            # обрабатываем сообщение

            # если сообщение хоть что-то содержит
            if len(incoming_message):
                # если это уведомление об отключении
                if incoming_message == self.__DISCONNECT_MSG:
                    # убираем пользователя из активных клиентов
                    self.active_clients.remove((conn, addr))

                    # прекращаем обслуживание клиента
                    connected = False

                    # отображаем это действие на сервере
                    print(f"\n[CONNECTIONS] ({addr[0]}) disconnected.\n")

                    # переадресуем это сообщение всем активным клиентам
                    message = f'\n[CONNECTIONS] {addr} has left the chat.\n'
                    message = message.encode(self.__FORMAT)
                    for client in self.active_clients:
                        client[0].send(message)

                # если это обычное сообщение
                else:
                    # печатаем сообщение на сервере
                    incoming_message = f"[{addr[0]}, {addr[1]}] {incoming_message}"
                    print(incoming_message)

                    # переадресуем это сообщение всем клиентам, включая отправителя (для подтверждения)
                    incoming_message = incoming_message.encode(self.__FORMAT)
                    for client in self.active_clients:
                        client[0].send(incoming_message)

    def start(self):
        # начинаем слушать входящие запросы, сообщения и т.п.
        self.__server.listen()
        cls()
        print(f"[LISTENING] Server started. Server is listening on {self.__ADDRESS}")

        # до конца работы программы
        while True:
            # принимаем каждого, кто хочет подключиться, и записываем его данные
            conn, addr = self.__server.accept()

            # выводим сообщение о новом пользователе на экран
            new_con_message = f"\n[NEW CONNECTION] {addr} connected.\n"
            print(new_con_message)

            # оповестим всех активных клиентов об этом
            new_con_message = new_con_message.encode(self.__FORMAT)
            for client in self.active_clients:
                client[0].send(new_con_message)

            # добавляем нового пользователя в список активных пользователей
            self.active_clients.append((conn, addr))

            # будем обслуживать каждого клиента отдельно
            thread = threading.Thread(target=self.__handle_client__, args=(conn, addr))
            thread.start()


if __name__ == "__main__":
    s = Server()
    s.start()
