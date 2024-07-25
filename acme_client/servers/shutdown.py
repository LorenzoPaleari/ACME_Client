import logging
import os
import sys

from flask import Flask
from configuration import Config
from main import stop

port = Config.SHUT_SERVER_PORT.value

cli = sys.modules['flask.cli']
cli.show_server_banner = lambda *x: None

app = Flask(__name__)

log = logging.getLogger(f"Main.werkzeug")
log.setLevel(logging.ERROR)


@app.route("/shutdown")
def main() -> str:
    os.remove("./key.pem")
    os.remove("./certificate.pem")
    stop()
    return "shutting down"


def shutdown_server_start(ip: str) -> None:
    app.run(host=ip, port=port, debug=False, use_reloader=False)