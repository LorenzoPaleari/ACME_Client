import subprocess
import sys
import shlex
import requests
import threading
import time
import ssl
import signal
import os
import socket
from cryptography import x509
from cryptography.hazmat.primitives import serialization
import logging
from pathlib import Path

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

stop_event = threading.Event()

# Function to parse command-line arguments
def parse_args():
    if len(sys.argv) != 2:
        print("Usage: python3 <script> <command_string>")
        sys.exit(1)
    return sys.argv[1]

def run_command(cmd):
    """Function to run the command with a timeout."""
    try:
        # Start the subprocess
        process = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)
        
        # Poll the process at intervals
        while process.poll() is None:
            if stop_event.is_set():
                # Terminate the process if stop_event is set
                print("Stopping process...")
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)  # Terminate the process group
                process.wait()  # Ensure process has terminated
                print("Process terminated.")
                return

            time.sleep(1)  # Poll every second

        # Get process output and handle results
        stdout, stderr = process.communicate()
        print(stdout.decode())
        if process.returncode != 0:
            print(f"Test failed! Error: {stderr.decode()}")
    
    except Exception as e:
        print(f"Error occurred: {e}")

def check_certificate_and_shutdown(timeout_duration):
    """ Function to periodically check the server certificate and handle shutdown. """
    url = "https://0.0.0.0:5001/"
    cert_url = "0.0.0.0"
    shutdown_url = "http://0.0.0.0:5003/shutdown"
    start_time = time.time()
    
    while True:
        if time.time() - start_time > timeout_duration:
            print("Timeout reached. Shutting down server.")
            shutdown_server()
            sys.exit(1)
        try:
            response = requests.get(url, verify=False)
            logger.info(f"Response status code: {response.status_code}")
            if response.status_code == 200:
                # Perform checks on the certificate here
                if check_certificate(cert_url):
                    print("Certificate is correct. Shutting down server.")
                    requests.post(shutdown_url)
                    sys.exit(0)
                    break
                else:
                    print("Certificate check failed.")
                    shutdown_server()
                    sys.exit(1)
            else:
                print(f"Failed to get certificate, status code: {response.status_code}")
        except requests.RequestException as e:
            pass
        
        time.sleep(5)  # Wait for 5 seconds before the next check

def get_certificate(hostname, port=443):
    """Retrieve the SSL certificate of a website, bypassing certificate validation."""
    # Create a default SSL context
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    
    # Connect to the server and retrieve the certificate
    with socket.create_connection((hostname, port)) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            # Get the peer certificate in DER format
            cert_bin = ssock.getpeercert(binary_form=True)
            
            if not cert_bin:
                raise Exception("Failed to retrieve certificate.")
            
            # Load the certificate using cryptography library
            cert = x509.load_der_x509_certificate(cert_bin)
            pem_cert = cert.public_bytes(encoding=serialization.Encoding.PEM)
            return pem_cert.decode('utf-8')

def check_certificate(certificate_url):
    """ Placeholder function to validate the certificate. """
    try:
        cert = get_certificate(certificate_url, 5001)
    except Exception as e:
        print(f"Failed to get certificate: {e}")
        return False
    #TODO:
    # Perform checks on the certificate - issuer, domain, expiration, revokation, etc.
    print(cert)
    return True

def shutdown_server():
    """ Function to call the server shutdown endpoint. """
    shutdown_url = "http://0.0.0.0:5003/shutdown"
    try:
        requests.post(shutdown_url)
        stop_event.set()
        sys.exit(1)
    except requests.RequestException as e:
        print(f"Shutdown request failed: {e}")

if __name__ == "__main__":
    command_string = parse_args()
    # Construct the command to be executed
    dir_path = Path(__file__).absolute()
    script = dir_path.parent.parent / "project/run"
    cmd = f"{script} {command_string}"

    timeout_duration = 120  # Set your desired timeout duration in seconds

    # Start the thread to run the command
    command_thread = threading.Thread(target=run_command, args=(cmd,))
    command_thread.start()

    # Start the thread to periodically check the certificate
    check_thread = threading.Thread(target=check_certificate_and_shutdown, args=(timeout_duration,))
    check_thread.start()

    check_thread.join()
    # Kill command thread if it is still running
    stop_event.set()
    command_thread.join()
    
    # Wait for the check thread to finish
    print("Process completed.")

