#!/usr/bin/env bash

MOCK_STATUS_FILE='tests/mock_status_file.txt'
MOCK_DATA_FILE='tests/mock_data_file.txt'

DAPP_STATUS_FILE=$1
DAPP_DATA_FILE=$2

cat $MOCK_STATUS_FILE > $DAPP_STATUS_FILE
cat $MOCK_DATA_FILE > $DAPP_DATA_FILE
