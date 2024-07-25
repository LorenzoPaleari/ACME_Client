def createCert(key_pem, cert_pem):
    with open("./certificate/key.pem", 'w') as f:
        f.write(key_pem)

    f.close()

    with open("./certificate/certificate.pem", 'w') as f:
        f.write(cert_pem)

    f.close()
