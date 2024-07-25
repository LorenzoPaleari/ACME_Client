from typing import List, Tuple

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.x509.oid import NameOID
from .jws import safe64encode


def cert_key_generation() -> rsa.RSAPrivateKey:
    private_key = rsa.generate_private_key(
        65537,
        2048
    )

    return private_key


def get_csr(domains: List[str]) -> Tuple[str, str]:
    domainArray = []
    for domain in domains:
        domainArray.append(x509.DNSName(u"" + domain))

    private_key = cert_key_generation()

    csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"CH"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Zurich"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"Zurich"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Network Security Project #1"),
        x509.NameAttribute(NameOID.COMMON_NAME, u"" + domains[0]),
    ])).add_extension(
        x509.SubjectAlternativeName(domainArray),
        critical=False,
    ).sign(private_key, hashes.SHA256())

    key_pem = private_key.private_bytes(Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())

    return safe64encode(csr.public_bytes(Encoding.DER)).decode(), key_pem.decode()
