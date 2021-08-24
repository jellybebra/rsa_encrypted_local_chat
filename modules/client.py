import socket
import sys
import threading
import time
import base64

if __name__ == '__main__':
    import rsa_module
    from find_host_ip import Network
    from constants import *  # тут есть 'import os'
else:
    from modules import rsa_module
    from modules.find_host_ip import Network
    from modules.constants import *  # тут есть 'import os'


class Client:
    def __init__(self):
        # очищаем экран
        os.system('cls' if os.name == 'nt' else 'clear')

        # создаём сокет
        self.__PORT = Messaging.PORT
        self.__CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # доп. константы
        self.__BPM = Messaging.BPM
        self.__FORMAT = Messaging.FORMAT

        # опознавательные знаки
        self.__DISCONNECT_MSG = Messaging.DISCONNECT_MSG
        self.__WIDE_MSG = Messaging.WIDE_MSG
        self.__ENCRYPTED_MSG = Messaging.ENCRYPTED_MSG
        self.__KEY_REQUEST_MSG = Messaging.KEY_REQUEST_MSG
        self.__KEY_ANSWER_MSG = Messaging.KEY_ANSWER_MSG

        # просим имя
        # TODO: имя должно состоять из одного слова
        # TODO: имя не должно содержать встроенных строк (!d, !e и т.п.)
        self.__name: str = input(f"Please enter your name: {Style.GREEN1}")
        print(Style.WHITE)

        # переменные
        self.__connected = None
        self.__recipient_pub_key = None
        self.__private_key, self.__pub_key = rsa_module.gen_keys()  # генерируем ключи шифрования (bytes)

    def __identify__(self):
        """Отправляет имя, а потом ключ"""
        encoded_name: bytes = self.__name.encode(self.__FORMAT)
        pub_key: bytes = self.__pub_key

        self.__CLIENT.send(encoded_name)
        self.__CLIENT.send(pub_key)

    def __send__(self):
        while self.__connected:  # пока подключены
            input_msg: str = input()  # ждём новое сообщение от пользователя

            # TODO: если запрос ключа не удался, т.к. такого пользователя нет среди активных, надо это написать

            try:
                tags = [
                    self.__WIDE_MSG,
                    self.__ENCRYPTED_MSG,
                    self.__KEY_REQUEST_MSG,
                    self.__KEY_ANSWER_MSG
                ]
                # сообщение не должно быть пустым
                assert len(input_msg.split()) >= 1

                # сообщение не должно содержать тэги, кроме !d
                assert not any(tag in input_msg for tag in tags)

                # если это не сообщение об отключении, то оно должно быть формата: {получатель} {сообщение}
                if self.__DISCONNECT_MSG not in input_msg:
                    assert len(input_msg.split()) > 1
            except AssertionError:
                print(f'{Style.RED1}[ERROR]{Style.WHITE} Wrong format.')
            else:
                if self.__DISCONNECT_MSG in input_msg:
                    encoded_message: bytes = input_msg.encode(self.__FORMAT)
                    self.__CLIENT.send(encoded_message)

                    print(f'\n[CONNECTION] {Style.GREEN2}DISCONNECTED.{Style.WHITE}\n')
                    sys.exit()  # выключаемся

                else:  # message: {адресат} {сообщение}
                    input_msg: list = input_msg.split(' ')
                    recipient: str = input_msg[0]
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
                    encrypted_message = rsa_module.encrypt(self.__recipient_pub_key, message)
                    encoded_msg = f'{self.__ENCRYPTED_MSG} '.encode(self.__FORMAT) + encrypted_message  # bytes + bytes

                    # отсылаем сообщение
                    self.__CLIENT.send(encoded_msg)

    def __receive__(self):
        while self.__connected:  # пока подключены
            self.__CLIENT.settimeout(None)  # без этой строки не работает

            # принимаем новое сообщение: {префикс} {само сообщение}
            inbox: str = self.__CLIENT.recv(self.__BPM).decode(self.__FORMAT)

            # отбрасываем тэг
            for tag in [self.__WIDE_MSG, self.__KEY_ANSWER_MSG, self.__ENCRYPTED_MSG]:
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
                encrypted_message = encrypted_message.encode(self.__FORMAT)
                message = rsa_module.decrypt(self.__private_key, encrypted_message)

                if name == f'[{self.__name}]':
                    print(f'{Style.GREEN1}[you]{Style.WHITE} {message}')
                else:
                    print(f'{Style.RED2}{name}{Style.WHITE} {message}')

    def connect(self, ip=''):
        """
        Ищет сервер (если не задан) и подключается к нему.

        :param ip: если дали ip, то не ищет в локальной сети
        :return: успех операции
        """

        def connect_attempt(hosts: list):
            """
            Попытаться подключиться к кому-нибудь из списка.

            :return: успех/неудача
            """

            for host in hosts:
                print(f'[CONNECTING] Attempt to connect to {host}...', end=' ')

                try:
                    ADDRESS = (host, self.__PORT)
                    self.__CLIENT = socket.create_connection(ADDRESS, timeout=0.5)  # TODO: попробовать снизить таймаут
                except socket.timeout:
                    print(f'{Style.RED1}FAILED{Style.WHITE}.')
                else:  # если ошибок не появилось
                    self.__connected = True
                    print(f'{Style.GREEN2}SUCCEEDED{Style.WHITE}.')
                    break

        h = []  # hosts
        if ip != '':
            h = Network().scan()  # ищем хостов
        else:
            h.append(ip)

        # пытаемся подключиться
        connect_attempt(h)

        # перейдём в экран "после попыток подключения"
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"[CONNECTING] Connection "
              f"{f'{Style.RED1}FAILED' if not self.__connected else f'{Style.GREEN2}COMPLETED'}",
              end=f'{Style.WHITE}.\n')

        return self.__connected

    def start(self):
        # авторизируемся
        self.__identify__()

        send = threading.Thread(target=self.__send__)
        receive = threading.Thread(target=self.__receive__)

        # начинаем отправлять и принимать сообщения сообщения
        send.start()
        receive.start()

        # выводим правила пользования
        print(f'\nPlease, type "{Style.RED1}{self.__DISCONNECT_MSG}{Style.WHITE}" when you\'re done.'
              '\nMessage format: {recipient\'s name} {message}\n')


if __name__ == '__main__':
    cl = Client()

    if cl.connect():
        cl.start()
