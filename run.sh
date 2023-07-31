#!/bin/bash

VENV_PATH="/root/SpotifyHistory/venv/bin/activate"
PROJECT_PATH="/root/SpotifyHistory"
MAIN_LOG="/var/log/spotify_history/spotify_main.log"

timestamp=$(date +"%Y-%m-%d %H:%M:%S")

run_etl() {
    printf "%s INFO [$(basename $0) | Attempting python3 main.py --function etl]\n" "$timestamp" >> $MAIN_LOG

    source "$VENV_PATH"

    /root/SpotifyHistory/venv/bin/python3 "$PROJECT_PATH/main.py" --function etl 2>> $MAIN_LOG

    deactivate
}

if [ -z "$1" ]; then
    echo "Usage: $0 <function_name>"
    exit 1
fi

if [ "$1" = "etl" ]; then
    run_etl
else
    echo "Invalid function name. Only 'etl' is supported."
    exit 1
fi
