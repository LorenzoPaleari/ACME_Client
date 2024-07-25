# ACME Client

The ACME Client is a Python-based tool designed to manage the lifecycle of SSL/TLS certificates by interacting with ACME (Automated Certificate Management Environment) servers. This client simplifies securing web communications by automating the creation, revocation, and renewal of certificates.

Certificates generated using this tool can be found under `acme_client/certificate`

## Features
- HTTP/DNS challenge
- Certificate Creation
- Certificate Revocation

## Installation

### Testing
The testing environment can simulate a complete ACME challenge from the client to the server. By default, the project comes with a Docker implementation of Pebble (a simple ACME Server implementation). If you have your own ACME server, feel free to use that; just ensure the communication port is 14000.

For more information on using Docker, refer to [this guide](/scripts/pebble/README.md). Below is a simple summary of the necessary steps:
```bash
cd ./scripts/pebble
chmod +x docker-compose.sh

./docker-compose.sh
sudo ./docker-compose.sh  # On Linux
```
The command is blocking, so use a new terminal session to continue with testing/setup. Do not lose the LOCAL_ADDRESS printed out by the Docker configuration script.

For troubleshooting, follow the detailed instructions available [here](/scripts/pebble/README.md).

### Dependencies
This project uses the following dependencies:
- `requests`
- `cryptography`
- `dnslib`
- `Flask`
- `Werkzeug`

The testing script will create a virtual environment and install all dependencies. If you prefer to install them manually, follow this procedure:
```bash
# From the project root
python3 -m venv ./project/venv
source ./project/venv/bin/activate

pip install --upgrade pip
pip install -r ./project/packages.txt
```
## Usage

### Testing
The ACME Client includes an adapted test from those used in the course to evaluate the project. Starting the test is simple. After following the [Installation](#testing) instructions, proceed as follows:

Note that Host_IP represents the IP address from which the servers will be reachable. If you are using the provided Pebble with Docker, this value was printed during the Docker setup. For a local instance of Pebble, use 127.0.0.1.
```bash
chmod +x test.sh    # Make test.sh executable
./test.sh [Host_IP]
```

### Configuration
To use the ACME client outside the test case, run:
```bash
python3 ./acme_client/main.py [OPTIONS]
```

Below is a more detailed usage description. The `--revoke`, `--mode`, and `--dns_A` options are not required.
```
usage: main.py [-h] --dir DIR --record RECORD --domain DOMAIN [--revoke] [--mode MODE] [--dns_A DNS_A] challengeType

positional arguments:
  challengeType    http01 or dns01

options:
  -h, --help       show this help message and exit
  --dir DIR        ACME directory URL
  --record RECORD  IP address of the server
  --domain DOMAIN  Domain name(s) and/or wildcard(s)
  --revoke         Revoke certificate
  --mode MODE      Test or production mode. Default is production
  --dns_A DNS_A    DNS A record IP address
```
## Note
The original requests that I had to comply with are available [here](./_project-instructions/).

## Disclaimer

The ACME Client has been developed as part of the Network Security Course at ETH Zurich (ETHZ). It is designed primarily for educational purposes and is intended to be tested locally. While the client can be adapted for real-world use, it may lack the latest security features and updates typically required for production environments.

Users are advised to exercise caution and not rely on this software for critical or sensitive operations without first conducting a thorough review and implementing additional security measures. The project is provided as-is, and the developers make no guarantees regarding its suitability for any specific purpose.
