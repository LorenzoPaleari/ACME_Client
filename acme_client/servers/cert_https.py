import logging
import sys

from flask import Flask
from configuration import Config

port = Config.CERT_SERVER_PORT.value

cli = sys.modules['flask.cli']
cli.show_server_banner = lambda *x: None

app = Flask(__name__)

log = logging.getLogger('Main.werkzeug')


@app.route("/")
def main():
    return "test"


def cert_http_start(ip: str) -> None:
    app.run(host=ip, port=port, debug=False, use_reloader=False, ssl_context=("./certificate/certificate.pem", "./certificate/key.pem"))
