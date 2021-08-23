import socket
import sys
import threading
import time
import base64
from modules import rsa_module
from modules.find_host_ip import Network
from modules.constants import *

# TODO: если сообщение пустое, не реагировать


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

        # опознавательные знаки
        self.__DISCONNECT_MSG = Messaging.DISCONNECT_MSG
        self.__WIDE_MSG = Messaging.WIDE_MSG
        self.__ENCRYPTED_MSG = Messaging.ENCRYPTED_MSG
        self.__KEY_REQUEST_MSG = Messaging.KEY_REQUEST_MSG
        self.__KEY_ANSWER_MSG = Messaging.KEY_ANSWER_MSG

        # переменные
        self.__connected = None
        self.__recipient_pub_key = None
        self.__name = input(f"Please enter your name: {Style.GREEN1}")
        print(Style.WHITE)
        self.__priv_key, self.__pub_key = rsa_module.gen_keys()  # генерируем ключи шифрования (bytes)

    def __identify__(self):
        """Отправляет имя, а потом ключ"""
        encoded_name = self.__name.encode(self.__FORMAT)  # str -> bytes
        pub_key = self.__pub_key  # bytes

        self.__CLIENT.send(encoded_name)
        self.__CLIENT.send(pub_key)

    def __send__(self):
        # пока подключены
        while self.__connected:
            # ждём новое сообщение
            full_message = input()

            # если это сообщение об отключении
            if self.__DISCONNECT_MSG in full_message:
                # отправляем сообщение
                full_message = full_message.encode(self.__FORMAT)  # str -> bytes
                self.__CLIENT.send(full_message)

                # отображаем на экране
                print(f'\n[CONNECTION] {Style.GREEN2}Disconnected successfully.{Style.WHITE}\n')

                # выключаемся
                sys.exit()

            # если это просто сообщение
            else:
                # формат сообщения: {адресат} {сообщение}
                full_message = full_message.split(' ')
                recipient = full_message[0]
                del full_message[0]
                message = ' '.join(full_message)

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
        # пока подключены
        while self.__connected:
            self.__CLIENT.settimeout(None)  # TODO: проверить, работает ли без этой строки

            # принимаем новое сообщение: {префикс} {само сообщение}
            inbox = self.__CLIENT.recv(self.__BPM).decode(self.__FORMAT)

            # отбрасываем префикс
            for index in [self.__WIDE_MSG, self.__KEY_ANSWER_MSG, self.__ENCRYPTED_MSG]:
                if index in inbox:
                    break
            message = inbox.replace(f'{index} ', '')  # TODO: проверить, работает это или нужно запихнуть обратно в цикл

            if index == self.__WIDE_MSG:
                print(message)  # выводим на экран

            if index == self.__KEY_ANSWER_MSG:
                # полученное сообщение - это закодированный ключ; записываем его, чтобы использовать в __send__
                self.__recipient_pub_key = base64.b64decode(message)

            if index == self.__ENCRYPTED_MSG:  # сообщение: [{name}] {encrypted message}
                # запишем имя и сообщение
                name, encrypted_message = message.split(' ')
                encrypted_message = encrypted_message.encode(self.__FORMAT)
                message = rsa_module.decrypt(self.__priv_key, encrypted_message)

                # выведем на экран
                if name == f'[{self.__name}]':
                    print(f'{Style.GREEN1}[you]{Style.WHITE} {message}')
                else:
                    print(f'{Style.RED2}{name}{Style.WHITE} {message}')

    def connect(self):
        """
        Ищем сервер и подключаемся к нему.
        Ничего не трогай. Работает.

        :return: успех операции
        """

        def try_to_connect(hosts):
            """
            Попытаться подключиться
            :return: успех/неудача
            """

            # для каждого полученного адреса
            for host in hosts:
                # выводим сообщение о том, к какому адресу пытаемся подключиться
                print(f'[CONNECTING] Attempt to connect to {host}...', end=' ')

                try:
                    # пытаемся подключиться
                    ADDRESS = (host, self.__PORT)
                    self.__CLIENT = socket.create_connection(ADDRESS, timeout=0.5)

                    # если не появилась ошибка, значит подключились, запишем это
                    self.__connected = True

                    # выводим сообщение об успехе на экран
                    print(f'{Style.GREEN2}SUCCEEDED{Style.WHITE}.')

                    # прекращаем поиск
                    break

                # в случае неудачного подключения
                except:  # TODO: узнать че тут за ошибка
                    # выводим сообщение о неудаче на экран
                    print(f'{Style.RED1}FAILED{Style.WHITE}.')

        # пытаемся быстро подключиться
        hosts = Network().scan(mode='fast')
        try_to_connect(hosts)

        # # если не удалось
        # if not self.__connected:
        #     # выводим сообщение об этом
        #     print(f'[CONNECTING] {Style.RED1}Failed to connect to any host.{Style.WHITE} Going for a rescan...')
        #
        #     # пробуем еще раз, но безопасно
        #     hosts = Network().scan(mode='safe')
        #     try_to_connect(hosts)

        # сотрём всю хуйню, которую написали
        import os
        os.system('cls' if os.name == 'nt' else 'clear')

        # выводим результат этих махинаций
        print(f"[CONNECTING] Connection {f'{Style.RED1}FAILED{Style.WHITE}' if not self.__connected else f'{Style.GREEN2}COMPLETED{Style.WHITE}'}.")

        # возвращаем этот результат
        return self.__connected

    def start(self):
        # авторизируемся
        self.__identify__()

        # начинаем отправлять сообщения
        send = threading.Thread(target=self.__send__)
        send.start()

        # начинаем принимать сообщения
        receive = threading.Thread(target=self.__receive__)
        receive.start()

        # открываем пользовательский интерфейс
        print(f'\nPlease, type "{Style.BLUE1}{self.__DISCONNECT_MSG}{Style.WHITE}" when you\'re done.'
              '\nMessage format: {recipient\'s name} {message}\n')


if __name__ == '__main__':
    cl = Client()

    # если присоединились
    if cl.connect():
        # запускаем обмен сообщениями
        cl.start()
