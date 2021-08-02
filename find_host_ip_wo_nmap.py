import socket
from datetime import datetime


class Network(object):
    def __init__(self, ip=''):

        # ip = input('Please enter default IP address of router: ')
        # self.ip = ip

        MY_LOCAL_IP = socket.gethostbyname(socket.gethostname())
        ROUTER_IP = MY_LOCAL_IP.split('.')
        ROUTER_IP[3] = '1'
        ROUTER_IP = '.'.join(ROUTER_IP)
        self.ip = ROUTER_IP

        print(f'[NETWORK] {self.ip} is taken for default IP address of router.')

    def network_scanner(self):
        """Scans the local network for hosts. Returns list of IPs of the hosts in the local network."""

        def check(addr):
            """Checks if the given IP address is a host's IP address. Returns True or False."""

            # print(f'[SCANNING] Trying {addr}...')
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = s.connect_ex((addr, 135))
            if result == 0:
                return 1
            else:
                return 0

        print('[SCANNING] Scanning. Please wait...')
        t1 = datetime.now()

        net = self.ip.split('.')
        net.pop()
        net = '.'.join(net)

        hosts = []
        socket.setdefaulttimeout(.05)
        for ip in range(1, 255):
            address = f'{net}.{ip}'
            if check(address):
                hosts.append(address)
                print(f"[SCANNING] {address} is hosting.")

        t2 = datetime.now()
        print(f"[SCANNING] Scanning completed in: {t2 - t1}")

        return hosts


if __name__ == '__main__':
    N = Network()
    N.network_scanner()
