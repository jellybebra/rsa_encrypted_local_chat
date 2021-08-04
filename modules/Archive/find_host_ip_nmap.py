from nmap import PortScanner
import socket


class Network(object):
    def __init__(self, ip=''):
        # ip = input('Please enter default IP address of router: ')
        # self.ip = ip

        MY_LOCAL_IP = socket.gethostbyname(socket.gethostname())
        ROUTER_IP = MY_LOCAL_IP.split('.')
        ROUTER_IP[3] = '1'
        ROUTER_IP = '.'.join(ROUTER_IP)
        self.ip = ROUTER_IP
        print(f'[NMAP] {self.ip} is taken for default IP address of router.')

    def network_scanner(self):
        network = self.ip + '/24'
        print('[NMAP] Scanning the network for hosts...')

        nm = PortScanner()
        nm.scan(hosts=network, arguments='-sn')
        host_list = [(x, nm[x]['status']['state']) for x in nm.all_hosts()]
        # print(host_list)
        hl = []
        for host, status in host_list:
            hl.append(host)
            # print(f'Host\t{host}')
        return hl


if __name__ == "__main__":
    n = Network()
    print(n.network_scanner())
