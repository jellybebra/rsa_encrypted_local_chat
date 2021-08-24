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
        """
        # TODO: Переделать, чтоб возвращала строку.

        names = []
        for client in self.__active_clients:
            names.append(client['name'])
        return names

    def __wide_message__(self, message: str):
        """
        Отправляет данное сообщение всем активным пользователям.

        :param message: сообщение, которое вы хотите разослать
        """
        message: str = f'{self.__WIDE_MSG} {message}'  # добавляем тэг
        encoded_message: bytes = message.encode(self.__FORMAT)

        # отправляем каждому клиенту
        for client in self.__active_clients:
            client['conn'].send(encoded_message)

    def __handle_client__(self, connection, address, name: str):
        # чтоб жёлтым не горело
        recipient: str = str()
        recipient_pub_key: bytes = bytes()
        recipient_conn = None

        # будем обслуживать, пока не отключится
        connected = True
        while connected:
            try:
                inc_message: str = connection.recv(self.__BPM).decode(self.__FORMAT)  # получаем новое сообщение
            except ConnectionResetError:  # если соединение потеряно
                connected: bool = False  # прекращаем обслуживание клиента

                # удаляем его данные
                for num, client in enumerate(self.__active_clients):
                    if client['conn'] == connection:
                        self.__active_clients.pop(num)
                        break

                # выведем сообщение об отключении пользователе и активных пользователях
                removed_connection_msg = f'\n[CONNECTIONS] ({address[0]}, {name}) disconnected.' \
                                         f'\n[CONNECTIONS] Active users: {self.__active_names__()}\n'
                self.__wide_message__(removed_connection_msg)
                if __name__ == '__main__':
                    print(removed_connection_msg)
            else:
                # отбрасываем тэг
                for tag in [self.__DISCONNECT_MSG, self.__KEY_REQUEST_MSG, self.__ENCRYPTED_MSG]:
                    if tag in inc_message:
                        break
                message: str = inc_message.replace(f'{tag} ', '')

                if tag == self.__DISCONNECT_MSG:  # сообщение: {self.__DISCONNECT_MSG}
                    connected: bool = False  # прекращаем обслуживание клиента

                    # удаляем его данные
                    for num, client in enumerate(self.__active_clients):
                        if client['conn'] == connection:
                            self.__active_clients.pop(num)
                            break

                    # выведем сообщение об отключении пользователе и активных пользователях
                    removed_connection_msg = f'\n[CONNECTIONS] ({address[0]}, {name}) disconnected.' \
                                             f'\n[CONNECTIONS] Active users: {self.__active_names__()}\n'
                    self.__wide_message__(removed_connection_msg)
                    if __name__ == '__main__':
                        print(removed_connection_msg)

                elif tag == self.__KEY_REQUEST_MSG:
                    recipient: str = message  # сообщение: {self.__KEY_REQUEST_MSG} {recipient}

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
        print(f"{Style.CYAN1}[SERVER]{Style.WHITE} Server started {self.__ADDRESS}.")

        while True:
            # ждём и записываем данные нового подключения
            conn, address = self.__SERVER.accept()  # сокет, IP и порт
            name: str = conn.recv(self.__BPM).decode(self.__FORMAT)  # имя
            pub_key: bytes = conn.recv(self.__BPM)  # public key

            # обновляем активные подключения
            self.__active_clients.append(
                {
                    'conn': conn,
                    'address': address,
                    'name': name,
                    'pub_key': pub_key
                }
            )

            # выведем сообщение о новом пользователе и активных пользователях
            new_connection_msg = f'\n[CONNECTIONS] ({address[0]}, {name}) joined.' \
                                 f'\n[CONNECTIONS] Active users: {self.__active_names__()}\n'
            self.__wide_message__(new_connection_msg)
            if __name__ == '__main__':
                print(new_connection_msg)

            # начинаем обслуживать, обрабатывать данного клиента
            handle_client = threading.Thread(target=self.__handle_client__, args=(conn, address, name))
            handle_client.start()


if __name__ == "__main__":
    s = Server()
    s.start()
