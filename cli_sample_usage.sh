function dm () {
    python3 -m yagna_dapp_manager "$@"
}

echo "1. CURRENT APPS"
dm list

APP_ID_1=$(DAPP_RUNNER_EXEC=tests/assets/mock_dapp_runner.py dm start --config ttt.yml zzz.yml)
echo "2. STARTED APP $APP_ID_1"

echo "3. CURRENT APPS"
dm list

APP_ID_2=$(DAPP_RUNNER_EXEC=tests/assets/mock_dapp_runner.py dm start --config ttt.yml zzz.yml)
echo "4. STARTED APP $APP_ID_2"

echo "5. CURRENT APPS"
dm list

echo "6. STOPPING $APP_ID_1 WITH DEFAULT TIMEOUT (should succeed)"
dm stop --app-id $APP_ID_1

echo "7. STOPPING $APP_ID_2 WITH SHORT TIMEOUT (should fail)"
dm stop --app-id $APP_ID_2 --timeout 1

echo "7. KILLING  $APP_ID_2"
dm kill --app-id $APP_ID_2
