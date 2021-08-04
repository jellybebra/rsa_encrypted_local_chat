import socket
from datetime import datetime

"""

Проблемы:
1. Если в сети больше чем 254 компа, то возможно не сработает.
   https://stackoverflow.com/questions/11453378/get-network-address-and-network-mask-in-python
   https://stackoverflow.com/questions/936444/retrieving-network-mask-in-python/2649654
   
"""


class Network(object):
    def __init__(self, ip=''):
        # if ip != '':
        #     ip = input('Please enter default IP address of router: ')
        # self.ip = ip

        MY_LOCAL_IP = socket.gethostbyname(socket.gethostname())
        ROUTER_IP = MY_LOCAL_IP.split('.')
        ROUTER_IP[3] = '1'
        ROUTER_IP = '.'.join(ROUTER_IP)
        self.ip = ROUTER_IP

        print(f'[NETWORK] {self.ip} is taken for router\'s default IP address.')

    def network_scanner(self, tmout=.04):
        """
        Scans the local network for hosts. Returns list of IPs of the hosts in the local network.
        :param tmout: timeout for an address to reply
        :return: list of hosts in the network
        """

        def check(addr):
            """
            Checks if a given IP is a host's IP.
            :param addr: IP address
            :return: is this IP a host's IP
            """

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # result = s.connect_ex((addr, 5050))  # создаёт лишнее сообщение на сервере (типа присоединился)
            result = s.connect_ex((addr, 135))  # находит ВСЕХ хостов

            if result == 0:
                return True
            else:
                return False

        print('[SCANNING] Scanning. Please wait...')
        t1 = datetime.now()

        net = self.ip.split('.')
        net.pop()
        net = '.'.join(net)

        hosts = []
        socket.setdefaulttimeout(tmout)
        for ip in range(1, 255):
            address = f'{net}.{ip}'
            if check(address):
                hosts.append(address)
                print(f"[SCANNING] {address} is hosting.")
        socket.setdefaulttimeout(None)

        t2 = datetime.now()
        print(f"[SCANNING] Scanning completed in: {t2 - t1}")

        return hosts


if __name__ == '__main__':
    N = Network()
    N.network_scanner()
