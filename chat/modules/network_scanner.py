import socket
if __name__ == '__main__':
    from constants import Style
else:
    from .constants import Style


class Network(object):
    def __init__(self):
        # записываем IP сети, в которой находимся
        MY_LOCAL_IP = socket.gethostbyname(socket.gethostname())
        self.ROUTER_IP = '.'.join(MY_LOCAL_IP.split('.')[:-1]) + '.1'
        print(f'[SCANNING] {self.ROUTER_IP} is taken for the network\'s IP address.')

    def scan(self) -> list:
        """
        Scans the local network for hosts in the current subnet.

        :return: hosts in the network
        """

        def is_host(address) -> bool:
            """
            Checks if a given IP is a host's IP.

            :param address: IP address
            :return: is this IP a host's IP
            """

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # создаём сокет

            port = 135
            # 135  -> обнаруживаются ВСЕ хосты
            # 5050 -> создаётся лишнее сообщение на сервере: "Новое подключение"

            result = s.connect_ex((address, port))
            return True if result == 0 else False

        print('[SCANNING] Scanning. Please wait...')
        hosts: list = []  # сюда запишем результаты поиска
        net: str = '.'.join(self.ROUTER_IP.split('.')[:-1])  # сеть, что-то вроде '192.168.60'

        socket.setdefaulttimeout(.02)  # без этого не работает; .04 для 100% нахождения

        # начинаем перебор
        for n in range(1, 255):
            adr = f'{net}.{n}'
            if is_host(adr):  # если IP является (подозреваемым) сервером
                hosts.append(adr)  # записываем его
                print(f"[SCANNING] {adr} is hosting.")

        socket.setdefaulttimeout(None)  # без этого не работает
        print(f"[SCANNING] Scanning {Style.GREEN}COMPLETED{Style.WHITE}.")

        return hosts

if __name__ == '__main__':
    n = Network()
    n.scan()