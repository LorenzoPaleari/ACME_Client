#!/bin/bash

# Determine if the script is running on a Linux host
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
  DEFAULT_LOCAL_ADDRESS="172.17.0.1"
else
  DEFAULT_LOCAL_ADDRESS="127.0.0.1"
fi

# Run the alpine-test container
docker run -d --name alpine-test \
  --network bridge \
  alpine:latest \
  sh -c "while true; do sleep 3600; done"

# If not Linux host, install bind-tools and test host.docker.internal
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
  docker exec alpine-test sh -c "apk update && apk add bind-tools"
  DEFAULT_LOCAL_ADDRESS=$(docker exec alpine-test sh -c "dig +short host.docker.internal")
fi



# Specify the port for the DNS server
DNS_PORT="10053"

# Combine the IP address and port
LOCAL_ADDRESS="${1:-$DEFAULT_LOCAL_ADDRESS}:${2:-$DNS_PORT}"
IP_ADDRESS="${LOCAL_ADDRESS%:*}"
PORT="${LOCAL_ADDRESS##*:}"

# Print out the addresses for verification
printf "\n\n\e[32mUsing LOCAL_ADDRESS: $IP_ADDRESS\e[0m\n"
printf "\e[32mUsing PORT: $PORT\e[0m\n\n"

docker stop alpine-test
docker rm alpine-test

# Run the pebble container with the DNS server address and port
docker run --rm --name pebble \
  -p 14000:14000 \
  -p 15000:15000 \
  -e PEBBLE_VA_NOSLEEP=1 \
  --network bridge \
  ghcr.io/letsencrypt/pebble:latest \
  -config test/config/pebble-config.json -strict -dnsserver ${IP_ADDRESS}:${PORT}
