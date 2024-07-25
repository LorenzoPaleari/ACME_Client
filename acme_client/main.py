import argparse
import servers.dns as dns
from threading import Thread
import ACME_Client
from servers import shutdown

def stop():
    ACME_Client.flag = False


def init():
    parser = argparse.ArgumentParser()
    parser.add_argument('challengeType', type=str, help='http01 or dns01')
    parser.add_argument('--dir', type=str, required=True, help='ACME directory url')
    parser.add_argument('--record', type=str, required=True, help='IP address of the server')
    parser.add_argument('--domain', action='append', required=True, help='Domain name/s and/or wildcard/s')
    parser.add_argument('--revoke', action='store_true', required=False, help='Revoke certificate')
    parser.add_argument('--mode', type=str, required=False, default='prodcution', help='test or production mode. Default is production')
    parser.add_argument('--dns_A', type=str, required=False, default='172.17.0.1', help='DNS A record IP address')

    args = parser.parse_args()

    challengeType = 'dns-01'
    if args.__getattribute__('challengeType') == 'http01':
        challengeType = 'http-01'

    ip = args.__getattribute__('record')
    revoke = args.__getattribute__('revoke')

    dns_A = args.__getattribute__('dns_A_record')
    mode = args.__getattribute__('mode')

    if mode == 'test':
        dns_thread = Thread(target=dns.start_dns, args=(ip, dns_A,))
        dns_thread.start()

        shutdown_server = Thread(target=shutdown.shutdown_server_start, args=(ip,), daemon=True)
        shutdown_server.start()

    acme_thread = Thread(target=ACME_Client.start_client, args=(args.__getattribute__('dir'), args.__getattribute__('domain'), challengeType, ip, revoke))
    acme_thread.start()

    acme_thread.join()
    dns.flag = False
    dns_thread.join()


if __name__ == '__main__':
    init()
