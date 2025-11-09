#!/bin/bash
# run_on_pi.sh
# Quick script to run commands on Pi remotely

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: $0 <pi_ip> <command>"
    echo "Example: $0 192.168.1.100 'list'"
    echo "Example: $0 192.168.1.100 'flash --firmware firmware.bin'"
    exit 1
fi

PI_IP="$1"
shift
COMMAND="$@"

ssh "pi@$PI_IP" "cd ~/parallel_flash_esp32 && source venv/bin/activate && ./flashd.py $COMMAND"

