# Docker Script for Configuring Pebble Container

 - **Docker**: Ensure Docker is installed and running on your host machine.

## Overview

This script sets up and runs a `pebble` container, using a local DNS service for DNS resolution. It determines the appropriate local DNS address and port to use, which by default is `host.docker.internal:10053` on non-Linux hosts and `172.17.0.1:10053` on Linux hosts.

## Purpose

The main objective of this script is to simulate an ACME server using the `pebble` container. This simulation is crucial for testing and validating the ACME client that is the focus of the project. The DNS service used for ACME server resolution is expected to be running on your host machine, on port `10053`.

## Usage

### Basic Usage
```bash
./docker-compose.sh [LOCAL_ADDRESS] [PORT]
```
   - `LOCAL_ADDRESS` (Optional): The IP address of the DNS server running on your host. Defaults to `172.17.0.1` on Linux or `host.docker.internal` on other operating systems.
   - `PORT` (Optional): The port for the DNS server. Defaults to `10053`.

### Example

```bash
./script.sh 192.168.1.1 10553
```
This command configure the `pebble`container to use `192.168.1.1:10553` as the DNS server address and port.

## Default Values

- On Linux Hosts:

   + `172.17.0.1`
   + `10053`
- On Non-Linux Hosts (macOS, Windows, etc.):

  + `host.docker.internal`
  + `10053`

## Script Behavior

### On Linux Hosts:

 - The script uses the default local address `172.17.0.1` and port `10053` to connect to the DNS service running on your host.
 - It configures and runs the `pebble` container with these DNS settings.

### On Non-Linux Hosts:

 - The script starts a temporary `alpine-test` container to resolve the address `host.docker.internal` to the correct local DNS address.
 - It installs bind-tools in the `alpine-test` container, retrieves the DNS address, and then uses it for the `pebble` container.

### Cleanup

- The script will automatically stop and remove the `alpine-test` container after retrieving the DNS address. As well as `pebble` as soon as you stop the script.

## Troubleshooting

 - **DNS Resolution Issues**: Verify that the alpine-test container can access `host.docker.internal` and that your host's DNS service is correctly configured.
 - **Port Conflicts**: If there are port conflicts, change the DNS port in the script and Docker commands accordingly.

---- 

Feel free to adjust this script to better fit your project needs.