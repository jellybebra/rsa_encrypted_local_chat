import socket
import threading
import base64
import time
from requests import get

if __name__ == '__main__':
    from modules.constants import *
else:
    from .modules.constants import *


class Server:
    def __init__(self):
        import os
        os.system('cls' if os.name == 'nt' else 'clear')

        # создаём полный адрес сервера
        self.__PORT = Messaging.PORT
        self.__SERVER_IP = socket.gethostbyname(socket.gethostname())
        try:
            self.__PUBLIC_SERVER_IP = get('https://api.ipify.org').text
        except:
            self.__PUBLIC_SERVER_IP = 'No connection.'
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
        self.__WIDE_MSG = Messaging.WIDE_MSG
        self.__ENCRYPTED_MSG = Messaging.ENCRYPTED_MSG
        self.__KEY_REQUEST_MSG = Messaging.KEY_REQUEST_MSG
        self.__KEY_ANSWER_MSG = Messaging.KEY_ANSWER_MSG
        self.__ACTIVE_CLIENTS_MSG = Messaging.ACTIVE_CLIENTS_MSG

    def __active_names__(self) -> str:
        """
        :return: список-строку активных пользователей через пробел
        """

        names: list = []

        for client in self.__active_clients:
            names.append(f'{client["name"]}')
        names: str = ' '.join(names)

        return names

    def __wide_message__(self, message: str):
        """
        Отправляет данное сообщение всем активным пользователям.

        :param message: сообщение, которое вы хотите разослать
        """

        message: str = f'{self.__WIDE_MSG} {message}'  # добавляем тэг
        encoded_message: bytes = message.encode(self.__FORMAT)
        for client in self.__active_clients:
            client['conn'].send(encoded_message)

    def __update_names__(self) -> None:
        """
        Обновляет доступных адресатов у всех клиентов.

        :return: None
        """

        message: str = f'{self.__ACTIVE_CLIENTS_MSG} {self.__active_names__()}'  # добавляем тэг
        encoded_message: bytes = message.encode(self.__FORMAT)
        for client in self.__active_clients:
            client['conn'].send(encoded_message)

        if __name__ == '__main__':
            print(f'[CONNECTIONS] Active users: {self.__active_names__()}')

    def __handle_client__(self, connection, address, name: str):
        # чтоб жёлтым не горело
        recipient: str = ''
        recipient_pub_key: bytes = bytes()
        recipient_conn = None

        # будем обслуживать, пока не отключится
        connected = True
        while connected:
            try:
                # получаем новое сообщение
                inc_message: str = connection.recv(self.__BPM).decode(self.__FORMAT)

            # если соединение потеряно
            except ConnectionResetError:
                connected: bool = False  # прекращаем обслуживание клиента

                for num, client in enumerate(self.__active_clients):  # удаляем его данные
                    if client['conn'] == connection:
                        self.__active_clients.pop(num)
                        break

                # оповещение (дисконнект пользователя, активные клиенты)
                removed_connection_msg = f'\n[CONNECTIONS] ({address[0]}, {name}) disconnected.'
                self.__wide_message__(removed_connection_msg)
                if __name__ == '__main__':
                    print(removed_connection_msg)
                self.__update_names__()

            else:
                # разделяем тэг и сообщение
                for tag in [self.__KEY_REQUEST_MSG, self.__ENCRYPTED_MSG]:
                    if tag in inc_message:
                        break
                message: str = inc_message.replace(f'{tag} ', '')

                if tag == self.__KEY_REQUEST_MSG:
                    recipient: str = message  # сообщение: {recipient}

                    # ищем ключ и сокет адресата
                    for client in self.__active_clients:
                        if client['name'] == recipient:
                            recipient_pub_key: bytes = client['pub_key']
                            recipient_conn = client['conn']
                            break

                    # отправляем ключ
                    recipient_pub_key: bytes = base64.b64encode(recipient_pub_key)  # bytes -> bytes
                    tag_and_key: bytes = f'{self.__KEY_ANSWER_MSG} '.encode(self.__FORMAT) + recipient_pub_key
                    connection.send(tag_and_key)

                elif tag == self.__ENCRYPTED_MSG:  # сообщение: {self.__ENCRYPTED_MSG} {encrypted encoded message}
                    if __name__ == '__main__':
                        print(f'[{name}] to [{recipient}]: {message}')

                    # добавим в сообщение имя отправителя
                    encrypted_message: bytes = message.encode(self.__FORMAT)
                    new_message: bytes = f'{self.__ENCRYPTED_MSG} [{name}] '.encode(self.__FORMAT) + encrypted_message

                    # пересылаем новое сообщение адресату
                    recipient_conn.send(new_message)

    def start(self):
        self.__SERVER.listen()  # слушаем порт
        print(f"{Style.CYAN}[SERVER]{Style.WHITE} Server started.\n"
              f"{Style.CYAN}[SERVER]{Style.WHITE} Private IP address: {self.__SERVER_IP}:{self.__PORT}.\n"
              f"{Style.CYAN}[SERVER]{Style.WHITE} Public IP address: {self.__PUBLIC_SERVER_IP}:{self.__PORT}.")

        while True:
            # ждём и записываем данные нового подключения
            conn, address = self.__SERVER.accept()  # сокет, IP и порт

            try:
                name: str = conn.recv(self.__BPM).decode(self.__FORMAT)  # имя
                pub_key: bytes = conn.recv(self.__BPM)  # public key
            except:
                # если что-то пошло не так, игнорим этого чела
                continue

            # обновляем активные подключения
            self.__active_clients.append(
                {
                    'conn': conn,
                    'address': address,
                    'name': name,
                    'pub_key': pub_key
                }
            )

            # начинаем обслуживать, обрабатывать данного клиента
            handle_client = threading.Thread(target=self.__handle_client__, args=(conn, address, name))
            handle_client.start()

            # оповещение (дисконнект пользователя, активные клиенты)
            new_connection_msg = f'\n[CONNECTIONS] ({address[0]}, {name}) joined.'
            self.__wide_message__(new_connection_msg)

            time.sleep(0.1)
            # не убирай, иначе соединятся 2 пакета и у клиенту придёт:
            # !w \n[CONNECTIONS] (192.168.60.61, ll) joined.\n !ac ll

            if __name__ == '__main__':
                print(new_connection_msg)
            self.__update_names__()


if __name__ == "__main__":
    while True:  # при возникновении ошибки перезапускается
        try:
            s = Server()
            s.start()
        except:
            print(f'{Style.RED1}[ERROR]{Style.WHITE} Unknown. Restarting the server...')
            time.sleep(5)
