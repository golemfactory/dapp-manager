function dm () {
    python3 -m yagna_dapp_manager "$@"
}

echo "CURRENT APPS"
dm list

APP_ID=$(DAPP_RUNNER_EXEC=tests/assets/mock_dapp_runner.py dm start --config ttt.yml zzz.yml)
# APP_ID=$(DAPP_RUNNER_EXEC=tests/assets/mock_dapp_runner.py python3 -m yagna_dapp_manager start --config ttt.yml zzz.yml)
echo "STARTED APP $APP_ID"

echo "CURRENT APPS"
dm list
