function dm () {
    python3 -m yagna_dapp_manager "$@"
}

echo "1. Current apps"
dm list

APP_ID_1=$(DAPP_RUNNER_EXEC=tests/assets/mock_dapp_runner.py dm start --config ttt.yml zzz.yml)
echo "2. Started app $APP_ID_1"

echo "3. Current apps"
dm list

APP_ID_2=$(DAPP_RUNNER_EXEC=tests/assets/mock_dapp_runner.py dm start --config ttt.yml zzz.yml)
echo "4. Started app $APP_ID_2"

echo "5. Current apps"
dm list

echo "6. Stopping $APP_ID_1 with default timeout (should succeed -> app_id printed)"
dm stop --app-id $APP_ID_1

echo "7. Stopping $APP_ID_2 with default timeout (should fail -> no print)"
dm stop --app-id $APP_ID_2 --timeout 1

echo "7. Killing  $APP_ID_2"
dm kill --app-id $APP_ID_2
