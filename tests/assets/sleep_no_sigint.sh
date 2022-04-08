#!/usr/bin/env bash

# Capture & ignore SIGINT (== Ctrl+C == KeyboardInterrupt)
trap 'echo "SIGINT ignored sorry"' INT

for ((n=$1; n; n--))
do
    sleep 1
done
