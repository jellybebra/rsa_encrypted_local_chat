import socket
import threading
import time
import base64
if __name__ == '__main__':
    from modules import encryption
    from modules.network_scanner import Network
    from modules.constants import *
else:  # если используется как модуль
    from .modules import encryption
    from .modules.network_scanner import Network
    from .modules.constants import *


class Client:
    def __init__(self):
        # очищаем экран
        import os
        os.system('cls' if os.name == 'nt' else 'clear')

        # создаём сокет
        self.__PORT = Messaging.PORT
        self.__CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # доп. константы
        self.__BPM = Messaging.BPM
        self.__FORMAT = Messaging.FORMAT

        # тэги сообщений
        self.__WIDE_MSG = Messaging.WIDE_MSG
        self.__ENCRYPTED_MSG = Messaging.ENCRYPTED_MSG
        self.__KEY_REQUEST_MSG = Messaging.KEY_REQUEST_MSG
        self.__KEY_ANSWER_MSG = Messaging.KEY_ANSWER_MSG
        self.__ACTIVE_CLIENTS_MSG = Messaging.ACTIVE_CLIENTS_MSG
        self.__TAGS = [
            self.__WIDE_MSG,
            self.__ENCRYPTED_MSG,
            self.__KEY_REQUEST_MSG,
            self.__KEY_ANSWER_MSG,
            self.__ACTIVE_CLIENTS_MSG
        ]

        # просим имя
        while True:
            name: str = input(f"Please enter your name: {Style.GREEN}")
            print(Style.WHITE, end='')

            try:
                assert len(name.split(' ')) == 1  # имя должно состоять из одного слова
                assert not any(tag in name for tag in self.__TAGS)  # в имени не должно быть тэгов
            except AssertionError:
                print(f'{Style.RED1}[ERROR]{Style.WHITE} Wrong format!')
            else:
                break
        self.__name = name

        # переменные
        self.__connected = None
        self.__recipient_pub_key = None
        self.__private_key, self.__pub_key = encryption.gen_keys()  # генерируем ключи шифрования (bytes)
        self.__active_names: list = []

    def __identify__(self):
        """Отправляет имя, а потом ключ"""
        encoded_name: bytes = self.__name.encode(self.__FORMAT)
        pub_key: bytes = self.__pub_key

        self.__CLIENT.send(encoded_name)
        self.__CLIENT.send(pub_key)

    def __send__(self):
        while self.__connected:
            input_msg: str = input()  # ждём новое сообщение от пользователя

            try:
                # сообщение не должно быть пустым
                assert len(input_msg.split()) >= 1

                # сообщение не должно содержать тэги
                assert not any(tag in input_msg for tag in self.__TAGS)

                # сообщение должно состоять минимум из 2х слов: {получатель} {сообщение}
                assert len(input_msg.split()) >= 2

            except AssertionError:
                print(f'{Style.RED1}[ERROR]{Style.WHITE} Wrong format.')
            else:
                # message: {адресат} {сообщение}
                input_msg: list = input_msg.split(' ')
                recipient: str = input_msg[0]

                try:
                    assert recipient in self.__active_names  # TODO: проверка на наличие получателя в активных юзерах
                except AssertionError:
                    print(f'{Style.RED1}[ERROR]{Style.WHITE} No such person on the server.')
                else:
                    message: str = ' '.join(input_msg[1:])

                    # шлём запрос на ключ
                    key_request = f'{self.__KEY_REQUEST_MSG} {recipient}'.encode(self.__FORMAT)
                    self.__CLIENT.send(key_request)

                    # подождём пока self.__receive__ получит ключ и запишет в self.__recipient_pubkey
                    time.sleep(0.5)
                    # TODO: попробовать уменьшить время / переделать типа:
                    #  while time.now() != времени последнего изменения переменной
                    #       pass

                    # шифруем сообщение
                    encrypted_message = encryption.encrypt(self.__recipient_pub_key, message)
                    encoded_msg = f'{self.__ENCRYPTED_MSG} '.encode(self.__FORMAT) + encrypted_message  # bytes + bytes

                    # отсылаем сообщение
                    self.__CLIENT.send(encoded_msg)

    def __receive__(self):
        while self.__connected:  # пока подключены
            self.__CLIENT.settimeout(None)  # без этой строки не работает

            try:
                # принимаем новое сообщение: {префикс} {само сообщение}
                inbox: str = self.__CLIENT.recv(self.__BPM).decode(self.__FORMAT)

            # если сервер сломался
            except ConnectionResetError:
                self.__connected = False
                print(f'[CONNECTIONS] Server {Style.RED1}disconnected{Style.WHITE}.')
                time.sleep(1)
                raise SystemExit

            else:
                # отделяем тэг от сообщения
                tag: str = ''
                for tag in self.__TAGS:
                    if tag in inbox:
                        break
                message: str = inbox.replace(f'{tag} ', '')

                if tag == self.__WIDE_MSG:
                    print(message)

                elif tag == self.__KEY_ANSWER_MSG:
                    self.__recipient_pub_key = base64.b64decode(message)  # записываем, чтобы использовать в __send__

                elif tag == self.__ENCRYPTED_MSG:  # сообщение: [{name}] {encrypted message}
                    name, encrypted_message = message.split(' ')
                    # кодируем обратно (т.к. случано эту часть раскодировали)
                    encrypted_encoded_message = encrypted_message.encode(self.__FORMAT)
                    message = encryption.decrypt(self.__private_key, encrypted_encoded_message)

                    if name == f'[{self.__name}]':
                        print(f'{Style.GREEN}[you]{Style.WHITE} {message}')
                    else:
                        print(f'{Style.RED2}{name}{Style.WHITE} {message}')

                elif tag == self.__ACTIVE_CLIENTS_MSG:
                    self.__active_names: list = message.split(' ')
                    print(f'[CONNECTIONS] Active users: {self.__active_names}\n')

    def connect(self, hosts: list):
        """
        Ищет сервер среди заданного списка адресов и подключается к нему.

        :param hosts: список подозреваемых ip адресов
        :return: успех операции
        """

        # пытаемся подключиться
        for host in hosts:
            print(f'[CONNECTING] Attempt to connect to {host}...', end=' ')

            try:
                ADDRESS = (host, self.__PORT)
                self.__CLIENT = socket.create_connection(ADDRESS, timeout=0.5)  # TODO: попробовать снизить таймаут
            except socket.timeout:
                print(f'{Style.RED1}FAILED{Style.WHITE}: Timeout.')
            except:
                print(f'{Style.RED1}FAILED{Style.WHITE}: Other error.')
            else:  # если ошибок не появилось
                self.__connected = True
                print(f'{Style.GREEN}SUCCEEDED{Style.WHITE}.')
                break

        # перейдём в экран "после попыток подключения"
        # import os
        # os.system('cls' if os.name == 'nt' else 'clear')
        print(f"[CONNECTING] Connection "
              f"{f'{Style.RED1}FAILED' if not self.__connected else f'{Style.GREEN}COMPLETED'}",
              end=f'{Style.WHITE}.\n')

        return self.__connected

    def start(self):
        # авторизируемся
        self.__identify__()

        receive = threading.Thread(target=self.__receive__)
        send = threading.Thread(target=self.__send__)

        # начинаем отправлять и принимать сообщения сообщения
        receive.start()
        send.start()

        # выводим правила пользования
        rules = f'\n{Style.CYAN}Disconnection:{Style.WHITE} Close the app.' + \
                f'\n{Style.CYAN}Message format:{Style.WHITE} ' + '{recipient\'s name} {message} '
        print(rules)


if __name__ == '__main__':
    cl = Client()

    ip = input(f'Enter the IP address (or press Enter): {Style.GREEN}')
    print(f'{Style.WHITE}', end='')

    if ip == '':
        hosts = Network().scan()
    else:
        hosts = [ip]

    if cl.connect(hosts):
        cl.start()
