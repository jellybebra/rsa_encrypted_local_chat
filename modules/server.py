import socket
import threading
import base64

"""

В пред. версии была проверка на длину сообщения.

"""


class Server:
    def __init__(self):
        # создаём полный адрес сервера
        self.__PORT = 5050
        self.__SERVER_IP = socket.gethostbyname(socket.gethostname())
        self.__ADDRESS = (self.__SERVER_IP, self.__PORT)

        # создаём сокет на заданном адресе
        self.__SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__SERVER.bind(self.__ADDRESS)

        # доп. переменные
        self.__active_clients = list()  # список словарей с данными всех подключенных на данный момент клиентов

        # константы
        self.__BPM = 512  # Bits Per Message - число бит для кодир-я 1 сообщения (взяли максимальное из-за лени)
        self.__FORMAT = 'utf-8'  # кодировка

        # опознавательные знаки
        self.__DISCONNECT_MSG = '!d'
        self.__WIDE_MSG = '!w'
        self.__ENCRYPTED_MSG = '!e'
        self.__KEY_REQUEST_MSG = '!kr'
        self.__KEY_ANSWER_MSG = '!ka'

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

                # удаляем его данные
                for client in self.__active_clients:
                    if client['conn'] == conn:
                        del client
                        break

                # отображаем это действие на сервере
                rm_con_message = f'\n[CONNECTIONS] ({addr[0]}, {name}) disconnected.' \
                                 f'\n[CONNECTIONS] Active users: {self.__active_names__()}\n'
                print(rm_con_message)

                # уведомим всех активных клиентов
                self.__wide_message__(rm_con_message)

            # если это запрос на ключ
            elif self.__KEY_REQUEST_MSG in inc_message:
                # полученное сообщение: {self.__KEY_REQUEST_MSG} {recipient}

                # напечатаем запрос на экране
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
                print(f'[{name}] to [{recipient}] {inc_message}')

                # добавим в сообщение отправителя
                encr_message = inc_message.split(' ')[1].encode(self.__FORMAT)  # тут вроде не должно быть бага, т.к. щифр - непр. строка
                new_message = f'{self.__ENCRYPTED_MSG} [{name}] '.encode(self.__FORMAT) + encr_message

                # пересылаем новое сообщение адресату
                recipient_conn.send(new_message)

    def start(self):
        # открываем и слушаем порт
        self.__SERVER.listen()
        print(f"[LISTENING] Server started {self.__ADDRESS}.")

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
            print(new_conn_message)

            # уведомим всех о новом подключении и всех активных пользователях
            self.__wide_message__(new_conn_message)

            # начинаем обслуживать данного клиента
            handle_client = threading.Thread(target=self.__handle_client__, args=(conn, addr, name))
            handle_client.start()


if __name__ == "__main__":
    s = Server()
    s.start()
