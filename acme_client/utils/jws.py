import hashlib
import json
import requests
from typing import Union
from base64 import urlsafe_b64encode

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from configuration import Config


def safe64encode(raw: bytes) -> bytes:
    return urlsafe_b64encode(raw).replace(b"=", b"")


def key_generation():
    JoseMessage.private_key = rsa.generate_private_key(
        65537,
        2048
    )
    public_key = JoseMessage.private_key.public_key()
    e_temp = public_key.public_numbers().e
    n_temp = public_key.public_numbers().n
    JoseMessage.e = safe64encode(e_temp.to_bytes(length=3, byteorder="big"))
    JoseMessage.n = safe64encode(n_temp.to_bytes(length=256, byteorder="big"))


def jdk():
    if JoseMessage.e is None:
        key_generation()

    jdk_header = {
        "e": JoseMessage.e.decode(),
        "kty": "RSA",
        "n": JoseMessage.n.decode()
    }
    return jdk_header


def thumbPrint() -> str:
    hashed = hashlib.sha256(json.dumps(jdk(), separators=(",", ":")).encode()).digest()
    return safe64encode(hashed).decode()


def dnsDigest(key: str) -> str:
    digest = hashlib.sha256(key.encode()).digest()
    return safe64encode(digest).decode()


class JoseMessage:
    private_key = None
    e = None
    n = None

    def __init__(self, payload: Union[str, dict], nonce: str, url: str, jwk=None, kid=None):
        self.url = url
        self.payload = payload
        self.nonce = nonce
        self.jwk = jwk
        self.kid = kid

    def protectedHeader(self):
        protected_header = {}

        if self.jwk is not None:
            protected_header = {
                "alg": "RS256",
                "jwk": jdk(),
                "nonce": self.nonce,
                "url": self.url
            }
        if self.kid is not None:
            protected_header = {
                "alg": "RS256",
                "kid": self.kid,
                "nonce": self.nonce,
                "url": self.url
            }
        return json.dumps(protected_header, separators=(",", ":")).encode()

    def body(self):
        encodedHeader = safe64encode(self.protectedHeader())

        if self.payload != "":
            payloadJson = json.dumps(self.payload, separators=(",", ":")).encode()
        else:
            payloadJson = self.payload.encode()
        encodedPayload = safe64encode(payloadJson)

        sign_input = b".".join([encodedHeader, encodedPayload])
        signature = self.sign(sign_input)

        body = {
            "protected": encodedHeader.decode('utf-8'),
            "payload": encodedPayload.decode('utf-8'),
            "signature": safe64encode(signature).decode('utf-8')
        }

        return json.dumps(body, separators=(",", ":"))

    def sign(self, sign_input):
        return self.private_key.sign(
            data=sign_input,
            padding=padding.PKCS1v15(),
            algorithm=hashes.SHA256()
        )


def post_request(url: str, nonce: str, payload="", kid=None, jwk=None):
    header = {"Content-Type": "application/jose+json"}
    data = JoseMessage(payload, nonce, url, kid=kid)
    if jwk:
        data = JoseMessage(payload, nonce, url, jwk=jwk)

    r = requests.post(url,
                      data=data.body(),
                      headers=header,
                      verify=Config.PEM_CERT_PATH.value)

    new_nonce = r.headers.get('Replay-Nonce')
    if r.status_code == 400 and r.json().get("type") == "urn:ietf:params:acme:error:badNonce":
        return post_request(url, new_nonce, payload, kid, jwk)

    return r, new_nonce
