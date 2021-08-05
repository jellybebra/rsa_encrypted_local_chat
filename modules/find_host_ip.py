import socket
from datetime import datetime

"""

Проблемы:
1. Если в сети больше чем 254 компа, то возможно не сработает.
   https://stackoverflow.com/questions/11453378/get-network-address-and-network-mask-in-python
   https://stackoverflow.com/questions/936444/retrieving-network-mask-in-python/2649654
   
"""


class Network(object):
    def __init__(self):
        # записываем IP сети, в которой находимся
        MY_LOCAL_IP = socket.gethostbyname(socket.gethostname())
        ROUTER_IP = MY_LOCAL_IP.split('.')
        ROUTER_IP[3] = '1'
        ROUTER_IP = '.'.join(ROUTER_IP)
        self.ip = ROUTER_IP

        # выводим полученный IP на экран
        print(f'[SCANNING] {self.ip} is taken for the router\'s default IP address.')

    def network_scanner(self, mode='safe'):
        """
        Scans the local network for hosts.

        :param mode: defines the guaranty of finding a server
        :return: list of hosts in the network
        """

        # определяет гарантию нахождения сервера
        timeout = .04
        if mode == 'fast':
            timeout = .02

        def check(addr):
            """
            Checks if a given IP is a host's IP.
            :param addr: IP address
            :return: is this IP a host's IP
            """

            # создаём сокет
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = s.connect_ex((addr, 135))  # находит ВСЕХ хостов
            # result = s.connect_ex((addr, 5050))  # создаёт лишнее сообщение на сервере (типа присоединился)

            # возвращаем результат проверки
            if result == 0:
                return True
            else:
                return False

        # выводим на экран сообщение о начале поиска сервера
        print('[SCANNING] Scanning. Please wait...')

        # включаем секундомер
        t1 = datetime.now()

        # подготавливаем шаблон для перебора адресов
        net = self.ip.split('.')
        net.pop()
        net = '.'.join(net)
        # получили что-то вроде '192.168.60'

        # объявляем переменную для записи результата поиска
        hosts = []

        # не трогай, опасно
        socket.setdefaulttimeout(timeout)

        # начинаем перебор
        for ip in range(1, 255):
            address = f'{net}.{ip}'

            # если IP является (подозреваемым) сервером
            if check(address):
                # записываем его
                hosts.append(address)

                # выводим IP на экран
                print(f"[SCANNING] {address} is hosting.")

        # не трогай, опасно
        socket.setdefaulttimeout(None)

        # останавливаем таймер
        t2 = datetime.now()

        # выводим время поиска подозреваемых серверов на экран
        print(f"[SCANNING] Scanning completed in: {t2 - t1}")

        # возвращаем результат поиска
        return hosts


if __name__ == '__main__':
    N = Network()
    N.network_scanner()
