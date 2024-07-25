import time

from dnslib import RR, QTYPE, A, TXT
from dnslib.server import DNSServer, DNSLogger
from configuration import Config

global authKey

class CustomResolver:
    def __init__(self, zone: str):
        self.zone = zone

    def resolve(self, request, handler):
        reply = request.reply()
        qtype = QTYPE[request.q.qtype]
        if qtype == QTYPE.get('A'):
            reply.add_answer(RR(request.q.qname, QTYPE.A, rdata=A(self.zone), ttl=60))
        if qtype == QTYPE.get('TXT'):
            reply.add_answer(RR(request.q.qname, QTYPE.TXT, rdata=TXT(authKey), ttl=300))
        return reply


flag = True


def start_dns(ip: str, dns_A: str) -> None:
    resolver = CustomResolver(dns_A)
    logger = DNSLogger(log="-request,-reply,-truncated,-error")

    server = DNSServer(resolver, port=Config.DNS_PORT.value, address=ip, logger=logger)
    server.start_thread()

    while flag:
        time.sleep(5)

    server.stop()

if __name__ == '__main__':
    start_dns("0.0.0.0")