import socket
import threading
import base64
if __name__ == '__main__':
    from constants import *
else:
    from modules.constants import *


class Server:
    def __init__(self):
        # создаём полный адрес сервера
        self.__PORT = Messaging.PORT
        self.__SERVER_IP = socket.gethostbyname(socket.gethostname())
        self.__ADDRESS = (self.__SERVER_IP, self.__PORT)

        # создаём сокет на заданном адресе
        self.__SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__SERVER.bind(self.__ADDRESS)

        # доп. переменные
        self.__active_clients = list()  # список словарей с данными всех подключенных на данный момент клиентов

        # константы
        self.__BPM = Messaging.BPM
        self.__FORMAT = Messaging.FORMAT

        # опознавательные знаки
        self.__DISCONNECT_MSG = Messaging.DISCONNECT_MSG
        self.__WIDE_MSG = Messaging.WIDE_MSG
        self.__ENCRYPTED_MSG = Messaging.ENCRYPTED_MSG
        self.__KEY_REQUEST_MSG = Messaging.KEY_REQUEST_MSG
        self.__KEY_ANSWER_MSG = Messaging.KEY_ANSWER_MSG

    def __active_names__(self) -> list:
        """
        Возвращает список активных пользователей.
        Переделать, чтоб возвращала строку.
        """

        names = []
        for client in self.__active_clients:
            names.append(client['name'])
        return names

    def __wide_message__(self, msg: str):
        """
        Отправляет данное сообщение всем активным пользователям.

        :param msg: сообщение, которое вы хотите разослать
        """
        # добавляем опознавательный знак
        msg = f'{self.__WIDE_MSG} {msg}'

        # кодируем сообщение
        msg = msg.encode(self.__FORMAT)

        # отправляем каждому клиенту
        for client in self.__active_clients:
            client['conn'].send(msg)

    def __handle_client__(self, conn, addr, name: str):
        # инициализация всякой хрени, чтоб жёлтым не горело
        recipient = str()
        recipient_pub_key = bytes()
        recipient_conn = None

        # будем обслуживать, пока не отключится
        connected = True

        while connected:
            # принимаем новое сообщение (ждём)
            inc_message = conn.recv(self.__BPM).decode(self.__FORMAT)  # bytes -> str

            # если это сообщение об отключении
            if self.__DISCONNECT_MSG in inc_message:
                # полученное сообщение: {self.__DISCONNECT_MSG}

                # прекращаем обслуживание клиента
                connected = False

                # TODO: исправить кусок снизу -- он не удаляет нифига
                # удаляем его данные
                for client in self.__active_clients:
                    if client['conn'] == conn:
                        del client
                        break

                # отображаем это действие на сервере
                rm_con_message = f'\n[CONNECTIONS] ({addr[0]}, {name}) disconnected.' \
                                 f'\n[CONNECTIONS] Active users: {self.__active_names__()}\n'
                if __name__ == '__main__':
                    print(rm_con_message)

                # уведомим всех активных клиентов
                self.__wide_message__(rm_con_message)

            # если это запрос на ключ
            elif self.__KEY_REQUEST_MSG in inc_message:
                # полученное сообщение: {self.__KEY_REQUEST_MSG} {recipient}

                # напечатаем запрос на экране
                if __name__ == '__main__':
                    print(f'[{name}] {inc_message}')

                # вытаскиваем адресата
                recipient = inc_message.split(' ')[1]

                # ищем ключ и сокет адресата
                for client in self.__active_clients:
                    if client['name'] == recipient:
                        recipient_pub_key = client['pub_key']
                        recipient_conn = client['conn']
                        break

                # отправляем ключ (вот тут могут быть баги)
                recipient_pub_key = base64.b64encode(recipient_pub_key)  # bytes -> bytes
                answer = f'{self.__KEY_ANSWER_MSG} '.encode(self.__FORMAT) + recipient_pub_key  # bytes + bytes
                conn.send(answer)

            # если это зашифрованное сообщение
            elif self.__ENCRYPTED_MSG in inc_message:
                # полученное сообщение: {self.__ENCRYPTED_MSG} {encrypted encoded message}

                # напечатаем сообщение на экране
                if __name__ == '__main__':
                    print(f'[{name}] to [{recipient}] {inc_message}')

                # добавим в сообщение имя отправителя
                encr_message = inc_message.split(' ')[1].encode(self.__FORMAT)
                new_message = f'{self.__ENCRYPTED_MSG} [{name}] '.encode(self.__FORMAT) + encr_message

                # пересылаем новое сообщение адресату
                recipient_conn.send(new_message)

    def start(self):
        self.__SERVER.listen()  # слушаем порт
        print(f"{Style.CYAN1}[SERVER]{Style.WHITE} Server started {self.__ADDRESS}.")

        # пока не выключим программу,
        # обрабатываем каждое новое подключение
        while True:
            # ждём и записываем данные
            conn, addr = self.__SERVER.accept()  # сокет, IP и порт
            name = conn.recv(self.__BPM).decode(self.__FORMAT)  # имя (bytes -> str)
            pub_key = conn.recv(self.__BPM)  # public key (bytes)
            self.__active_clients.append(  # обновляем активные подключения
                {
                    'conn': conn,
                    'addr': addr,
                    'name': name,
                    'pub_key': pub_key
                }
            )

            # выведем сообщение о новом пользователе и активных пользователях
            new_conn_message = f'\n[CONNECTIONS] ({addr[0]}, {name}) joined.' \
                               f'\n[CONNECTIONS] Active users: {self.__active_names__()}\n'
            if __name__ == '__main__':
                print(new_conn_message)

            # уведомим всех о новом подключении и всех активных пользователях
            self.__wide_message__(new_conn_message)

            # начинаем обслуживать данного клиента
            handle_client = threading.Thread(target=self.__handle_client__, args=(conn, addr, name))
            handle_client.start()


if __name__ == "__main__":
    s = Server()
    s.start()
