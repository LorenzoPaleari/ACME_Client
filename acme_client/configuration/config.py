from enum import Enum


class Config(Enum):
    DNS_PORT = 10053
    CHALL_SERVER_PORT = 5002
    CERT_SERVER_PORT = 5001
    SHUT_SERVER_PORT = 5003
    PEM_CERT_PATH = "../project/pebble.minica.pem"
