#!/bin/bash

# Get ip address as first cli argument or use default value 172.17.0.1
dns_A_reply=${1:-"172.17.0.1"}

# Function to check if a port is active
check_port() {
    local host=$1
    local port=$2
    nc -z "$host" "$port" > /dev/null 2>&1
}

# PREPARATION

printf "Preparing the environment...\n"

printf " - Adding the execute permission to the scripts..."
# Add the execute permission to the scripts
find ./scripts -type f -iname "*.sh" -exec chmod +x {} \;
find ./scripts/pebble -type f -iname "*.sh" -exec chmod +x {} \;
find ./project -type f -iname "*.sh" -exec chmod +x {} \;
chmod +x ./project/compile ./project/run
printf "\e[32m DONE!\e[0m\n"

printf " - Installing python dependencies..."
./scripts/docker-compile.sh
printf "\e[32m DONE!\e[0m\n"

printf " - Starting pebble container...\n"

# Check if Pebble is already running
if check_port "localhost" 14000 && check_port "localhost" 15000; then
    printf "  \e[37mPebble is already running on ports 14000 and 15000.\e[0m\n"
else
    printf "  \e[37mPebble is not running. Please start the container.\e[0m\n"
    exit 1
fi

# Verify Pebble is running
if check_port "localhost" 14000 && check_port "localhost" 15000; then
    printf "  \e[32mPEBBLE IS RUNNING\e[0m\n"
else
    printf "  \e[31mPebble is not reachable on ports 14000 or 15000.\e[0m\n"
    exit 1
fi

printf "\e[32mEnvironment ready!\e[0m\n\n"







# Start ACME Client
printf "Starting Tests\n"

source ./project/venv/bin/activate

# List of test names
test_names=(
    "http-single-domain"
    "http-multi-domain"
    "dns-single-domain"
    "dns-multi-domain"
    "dns-wildcard-domain"
    "http-revocation"
    "dns-revocation"
)

# List of test commands (corresponding to the above test names)
test_commands=(
    "http01 --dir https://localhost:14000/dir --record 0.0.0.0 --domain example.com --mode test --dns_A $dns_A_reply "
    "http01 --dir https://localhost:14000/dir --record 0.0.0.0 --domain example.com --domain test.example.com --mode test --dns_A $dns_A_reply "
    "dns01 --dir https://localhost:14000/dir --record 0.0.0.0 --domain example.com --mode test --dns_A $dns_A_reply "
    "dns01 --dir https://localhost:14000/dir --record 0.0.0.0 --domain example.com --domain test.example.com --mode test --dns_A $dns_A_reply "
    "dns01 --dir https://localhost:14000/dir --record 0.0.0.0 --domain example.com --domain *.example.com --mode test --dns_A $dns_A_reply "
    "http01 --dir https://localhost:14000/dir --record 0.0.0.0 --domain example.com --revoke --mode test --dns_A $dns_A_reply "
    "dns01 --dir https://localhost:14000/dir --record 0.0.0.0 --domain example.com --revoke --mode test --dns_A $dns_A_reply "
)

# Initialize counters
pass_count=0
fail_count=0

# Path to the Python script
SCRIPT_PATH="./scripts/launcher.py"

# Loop through both lists
for i in "${!test_names[@]}"; do
    test_name="${test_names[$i]}"
    test_command="${test_commands[$i]}"
    
    printf " - Running test: %s" "$test_name"
    
    # Run the Python script with the test command
    python3 "$SCRIPT_PATH" "$test_command"
    
    # Check if the command was successful
    if [ $? -eq 0 ]; then
        printf "   \e[32m Test passed! \e[0m\n"
        ((pass_count++))
    else
        printf "   \e[31m Test failed! \e[0m\n"
        ((fail_count++))
    fi
done

# Print summary
total_tests=$((pass_count + fail_count))

if [ "$pass_count" -eq "$total_tests" ]; then
    status="Perfect"
    color="\e[32m"  # Green
elif [ "$fail_count" -le $((total_tests / 4)) ]; then
    status="Good"
    color="\e[33m"  # Yellow
else
    status="Bad"
    color="\e[31m"  # Red
fi

printf "\e[0mAll tests completed!\n"
printf "Total tests: %d\n" "$total_tests"
printf "Passed: %d\n" "$pass_count"
printf "Failed: %d\n" "$fail_count"
printf "${color}Status: %s\e[0m\n" "$status"