import socket
import sys
import threading
import rsa_module
import time
import base64
from find_host_ip import Network

"""

Попробовать понизить BPM для ускорения.

"""


class Client:
    def __init__(self):
        # создаём сокет
        self.__PORT = 5050
        self.__CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # доп. константы
        self.__BPM = 512  # Bits Per Message - число бит для кодир-я 1 сообщения (взяли максимальное из-за лени)
        self.__FORMAT = 'utf-8'  # кодировка

        # опознавательные знаки
        self.__DISCONNECT_MSG = '!d'
        self.__WIDE_MSG = '!w'
        self.__ENCRYPTED_MSG = '!e'
        self.__KEY_REQUEST_MSG = '!kr'
        self.__KEY_ANSWER_MSG = '!ka'

        # переменные
        self.__connected = None
        self.__recipient_pub_key = None
        self.__name = input("Please enter your name: ")
        self.__priv_key, self.__pub_key = rsa_module.gen_keys()  # генерируем ключи шифрования

    def __identify__(self):
        # отправляем имя
        name = self.__name.encode(self.__FORMAT)  # str -> bytes
        self.__CLIENT.send(name)

        # отправляем открытый ключ
        pub_key = self.__pub_key  # bytes
        self.__CLIENT.send(pub_key)

    def __send__(self):
        # пока подключены
        while self.__connected:
            # ждём новое сообщение
            full_message = input()

            # если это сообщение об отключении
            if self.__DISCONNECT_MSG in full_message:
                # отправляем сообщение
                self.__CLIENT.send(full_message.encode(self.__FORMAT))

                # отображаем на экране
                print('\n[CONNECTION] Disconnected.\n')

                # выключаемся
                sys.exit()

                # останавливаем цикл
                # self.__connected = False

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
                time.sleep(1)

                # шифруем сообщение
                encrypted_message = rsa_module.encrypt(self.__recipient_pub_key, message)
                encoded_msg = f'{self.__ENCRYPTED_MSG} '.encode(self.__FORMAT) + encrypted_message  # bytes + bytes

                # отсылаем сообщение
                self.__CLIENT.send(encoded_msg)

    def __receive__(self):
        # пока подключены
        while self.__connected:
            # не знаю почему, но без этой строки не работает - не трогай
            self.__CLIENT.settimeout(None)

            # принимаем новое сообщение (ждём)
            inc_message = self.__CLIENT.recv(self.__BPM).decode(self.__FORMAT)

            # если это широковещательное сообщение
            if self.__WIDE_MSG in inc_message:
                # полученное сообщение: {self.__WIDE_MSG} {MESSAGE}

                # отбрасываем префикс
                message = inc_message.replace(f'{self.__WIDE_MSG} ', '')

                # выводим на экран
                print(message)

            # если это ответ на запрос о ключе
            if self.__KEY_ANSWER_MSG in inc_message:
                # полученное сообщение: {self.__KEY_ANSWER_MSG} {recipient_pub_key}
                # тут может быть баг из-за того, что может раскодироваться

                # отделяем сам ключ
                recipient_pub_key = inc_message.split(' ')[1]

                # декодируем ключ
                recipient_pub_key = base64.b64decode(recipient_pub_key)

                # "отправляем" в __send__
                self.__recipient_pub_key = recipient_pub_key

            # если это зашифрованное сообщение
            if self.__ENCRYPTED_MSG in inc_message:
                # полученное сообщение: {self.__ENCRYPTED_MSG} [{name}] {encrypted message}

                # отбросим префикс
                inc_message = inc_message.replace(f'{self.__ENCRYPTED_MSG} ', '')

                # запишем имя и сообщение
                inc_message = inc_message.split(' ')
                name = inc_message[0]
                del inc_message[0]
                encrypted_message = ' '.join(inc_message).encode(self.__FORMAT)

                # расшифруем сообщение
                message = rsa_module.decrypt(self.__priv_key, encrypted_message)

                # выведем на экран
                print(f'{name} {message}')

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
                print(f'[CONNECTING] Trying to connect to {host}...')

                try:
                    # пытаемся подключиться
                    ADDRESS = (host, self.__PORT)
                    self.__CLIENT = socket.create_connection(ADDRESS, timeout=0.5)  # testing

                    # если не появилась ошибка, значит подключились, запишем это
                    self.__connected = True

                    # выводим сообщение об успехе на экран
                    print('[CONNECTING] Success.')

                    # прекращаем поиск
                    break

                # в случае неудачного подключения
                except:
                    # выводим сообщение о неудаче на экран
                    print(f'[CONNECTING] FAILED.')

        # пытаемся быстро подключиться
        hosts = Network().network_scanner(mode='fast')
        try_to_connect(hosts)

        # если не удалось
        if not self.__connected:
            # выводим сообщение об этом
            print('[CONNECTING] Failed. Going for a rescan...')

            # пробуем еще раз, но безопасно
            hosts = Network().network_scanner(mode='safe')
            try_to_connect(hosts)

        # выводим результат этих махинаций
        print(f"[CONNECTING] Connection {'FAILED' if not self.__connected else 'completed'}.")

        # сотрём всю хуйню, которую написали
        import os
        os.system('cls' if os.name == 'nt' else 'clear')

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
        print('\nPlease, type "!disconnect" when you\'re done.'
              '\nMessage format: {recipient\'s name} {message}\n')


if __name__ == '__main__':
    cl = Client()

    # если присоединились
    if cl.connect():
        # запускаем обмен сообщениями
        cl.start()
