import time
import requests
from threading import Thread

from cryptography import x509
from cryptography.hazmat.primitives.serialization import Encoding
from utils import post_request, thumbPrint, dnsDigest, safe64encode, get_csr, createCert
from configuration import Config
from servers import challenge_http, cert_http_start, dns

flag = True

def start_client(directoryUrl, domains, challengeType, ip, revoke):

    nonceUrl, newAccountUrl, newOrderUrl, revokeCertUrl = request_dir(directoryUrl)
    acme_nonce = request_first_nonce(nonceUrl)
    kid, acme_nonce = request_new_account(newAccountUrl, acme_nonce)
    orderUrl, finalizeUrl, authorizations, acme_nonce = request_order(newOrderUrl, acme_nonce, kid, domains)
    domains_ordered, challengesUrl, tokens, acme_nonce = get_tokens(authorizations, acme_nonce, kid, challengeType)

    keyAuthorization = []
    for value in tokens:
        keyAuthorization.append(".".join([value, thumbPrint()]))

    if challengeType == "http-01":
        challenge_http.authKey = keyAuthorization
        challenge_http.tokens = tokens

        challenge_process = Thread(target=challenge_http.challenge_http_start, args=(keyAuthorization, tokens, ip,), daemon=True)
        challenge_process.start()

    time.sleep(3)

    if challengeType == "dns-01":
        dns.authKey = dnsDigest(keyAuthorization[0])
    count = 1
    for url in challengesUrl:
        r, acme_nonce = post_request(url, acme_nonce, payload={}, kid=kid)
        if challengeType == "dns-01":
            r, acme_nonce = post_request(authorizations[count-1], acme_nonce, kid=kid)
            while r.json().get('status') != 'valid':
                time.sleep(5)
                r, acme_nonce = post_request(authorizations[count-1], acme_nonce, kid=kid)
            if len(challengesUrl) > count:
                dns.authKey = dnsDigest(keyAuthorization[count])
            count += 1

    r, acme_nonce = post_request(orderUrl, acme_nonce, kid=kid)
    while r.json().get('status') != 'ready':
        time.sleep(5)
        r, acme_nonce = post_request(orderUrl, acme_nonce, kid=kid)

    csr, key_pem = get_csr(domains)
    payload = {"csr": csr}

    r, acme_nonce = post_request(finalizeUrl, acme_nonce, payload=payload, kid=kid)
    while r.json().get('status') != 'valid':
        time.sleep(5)
        r, acme_nonce = post_request(orderUrl, acme_nonce, kid=kid)

    certificateUrl = r.json().get('certificate')
    r, acme_nonce = post_request(certificateUrl, acme_nonce, kid=kid)

    createCert(key_pem, r.text)
    cert_process = Thread(target=cert_http_start, args=(ip,), daemon=True)
    cert_process.start()

    if revoke:
        revoke_cert(r.text, revokeCertUrl, acme_nonce, kid)

    while flag:
        print(flag)
        time.sleep(5)

def revoke_cert(cert, revokeCertUrl, acme_nonce, kid):
    cert_pem = x509.load_pem_x509_certificate(cert.encode())
    cert_der = safe64encode(cert_pem.public_bytes(Encoding.DER)).decode()

    payload = {
        "certificate": cert_der
    }

    r, acme_nonce = post_request(revokeCertUrl, acme_nonce, payload=payload, kid=kid)


def request_dir(directoryUrl):
    r = requests.get(directoryUrl, verify=Config.PEM_CERT_PATH.value)
    return str(r.json().get('newNonce')), str(r.json().get("newAccount")), str(r.json().get("newOrder")), str(
        r.json().get("revokeCert"))


def request_first_nonce(nonceUrl):
    r2 = requests.get(nonceUrl,
                      verify=Config.PEM_CERT_PATH.value
                      )

    return r2.headers.get('Replay-Nonce')


def request_new_account(newAccountUrl, acme_nonce):
    acme_payload = {
        "termsOfServiceAgreed": True
    }

    r, nonce = post_request(newAccountUrl, acme_nonce, acme_payload, jwk=True)
    return r.headers.get('Location'), nonce


def request_order(newOrderUrl, nonce, kid, domains):
    identifiers = []
    for domain in domains:
        identifiers.append({
            "type": "dns",
            "value": domain
        })

    payload = {
        "identifiers": identifiers
    }

    r, acme_nonce = post_request(newOrderUrl, nonce, payload, kid=kid)
    return r.headers.get('Location'), r.json().get('finalize'), r.json().get('authorizations'), acme_nonce


def get_tokens(authorizations, acme_nonce, kid, challengeType):
    domains_ordered = []
    challengesUrl = []
    tokens = []
    for url in authorizations:
        r, acme_nonce = post_request(url, acme_nonce, kid=kid)
        domains_ordered.append(r.json().get('identifier').get('value'))
        for val in r.json().get('challenges'):
            if val.get('type') == challengeType:
                challengesUrl.append(val.get('url'))
                tokens.append(val.get('token'))

    return domains_ordered, challengesUrl, tokens, acme_nonce
