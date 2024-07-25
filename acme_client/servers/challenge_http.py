import sys
from typing import List

from flask import Flask
from configuration import Config

port = Config.CHALL_SERVER_PORT.value

cli = sys.modules['flask.cli']
cli.show_server_banner = lambda *x: None

app = Flask(__name__)

global authKey
global tokens

@app.route("/.well-known/acme-challenge/<token>")
def main(token: str) -> str:
    global authKey
    global tokens
    for tok in tokens:
        if tok == token:
            return authKey[tokens.index(tok)]

def challenge_http_start(key: List[str], tok: List[str], ip:str) -> None:
    global authKey
    global tokens
    authKey = key
    tokens = tok
    app.run(host=ip, port=port, debug=False, use_reloader=False)

if __name__ == '__main__':
    challenge_http_start(["test"], ["test"], "0.0.0.0")