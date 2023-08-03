#!/bin/bash

VENV_PATH="/root/SpotifyHistory/venv/bin/activate"
PROJECT_PATH="/root/SpotifyHistory"
MAIN_LOG="/var/log/spotify_history/spotify_main.log"

timestamp=$(date +"%Y-%m-%d %H:%M:%S")

activate_venv() {
    source "$VENV_PATH"
}

deactivate_venv() {
    deactivate
}

run_python_script() {
    function_name="$1"
    printf "%s INFO [$(basename $0) | Attempting python3 main.py --function $function_name\n" "$timestamp" >>"$MAIN_LOG"

    activate_venv

    /root/SpotifyHistory/venv/bin/python3 "$PROJECT_PATH/main.py" --function "$function_name" 2>>"$MAIN_LOG"

    deactivate_venv
}

run_etl() {
    run_python_script "etl"
}

print_summary() {
    run_python_script "summary"
}

random_playlist() {
    run_python_script "random_playlist"
}

yesterday() {
    run_python_script "yesterday"
}

if [ -z "$1" ]; then
    echo "Usage: $0 <function_name>"
    exit 1
fi

case "$1" in
"etl")
    run_etl
    ;;
"summary")
    print_summary
    ;;
"random_playlist")
    random_playlist
    ;;
"yesterday")
    yesterday
    ;;
*)
    echo "Invalid function name: $1"
    exit 1
    ;;
esac
