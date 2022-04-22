#!/usr/bin/env bash

MOCK_STATE_FILE='tests/assets/mock_state_file.txt'
MOCK_DATA_FILE='tests/assets/mock_data_file.txt'

DAPP_STATE_FILE=$1
DAPP_DATA_FILE=$2

cat $MOCK_STATE_FILE > $DAPP_STATE_FILE
cat $MOCK_DATA_FILE > $DAPP_DATA_FILE

#   This sleep is to pretend that this app is running for a "while"
#   (apps that return immediately require a special approach in tests,
#   because of the AppNotRunning exception).
sleep 1
