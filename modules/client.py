import os
import socket
import sys
import threading
from find_host_ip import Network


def cls():
    """
    Clears the screen.
    """
    os.system('cls' if os.name == 'nt' else 'clear')


class Client:
    def __init__(self):
        # создаём сокет
        self.__PORT = 5050
        self.__CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # доп переменные
        self.__BPM = 2048  # Bits Per Message - число бит для кодир-я 1 сообщения (взяли максимальное из-за лени)
        self.__FORMAT = 'utf-8'  # кодировка
        self.__DISCONNECT_MSG = '!disconnect'
        self.__connected = False

    def __send__(self):
        # открываем пользовательский интерфейс
        cls()
        print('Please, type "!disconnect" when you\'re done.\n')

        # пока подключены
        while self.__connected:
            # просим пользователя ввести сообщение
            message = input('')

            # отсылаем сообщение
            self.__CLIENT.send(message.encode(self.__FORMAT))

            # если сообщение - уведомление об отключении
            if message == self.__DISCONNECT_MSG:
                # записываем это
                self.__connected = False

                # отображаем на экране
                print('\n[CONNECTION] Disconnected.\n')

                # спрашиваем, хотим ли подключиться снова? --------- экспериментальная фича, могут быть баги
                answer = input('Press \'Enter\' if you\'d like to reconnect.\nType \'exit\' and press \'Enter\' if '
                               'you\'d like to exit.')
                if answer == '':
                    self.start()
                else:
                    sys.exit()

    def __receive__(self):
        # пока подключены
        while self.__connected:
            # не знаю почему, но без этой строки не работает - не трогай
            self.__CLIENT.settimeout(None)

            # ждём сообщение
            message = self.__CLIENT.recv(self.__BPM).decode(self.__FORMAT)

            # редактируем, чтобы можно было писать в ответ и выводим на экран
            message = f'{message}'
            print(message)

    def connect(self):
        """
        Ищем сервер и подключаемся к нему.
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

        # возвращаем этот результат
        return self.__connected

    def start(self):
        # подсоединяемся
        self.connect()

        # если подключились
        if self.__connected:
            # начинаем отправлять сообщения
            send = threading.Thread(target=self.__send__)
            send.start()

            # начинаем принимать сообщения
            receive = threading.Thread(target=self.__receive__)
            receive.start()


if __name__ == "__main__":
    c = Client()
    c.start()
