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

sleep 1

echo "6. Print state file for $APP_ID_1"
dm raw-state --app-id $APP_ID_1

echo "7. Print data file for $APP_ID_1"
dm raw-data --app-id $APP_ID_1

sleep 2

echo "8. Print state file for $APP_ID_1"
dm raw-state --app-id $APP_ID_1

echo "9. Print data file for $APP_ID_1"
dm raw-data --app-id $APP_ID_1

echo "10. Print data file for $APP_ID_2"
dm raw-data --app-id $APP_ID_2

echo "11. Stopping $APP_ID_1 with default timeout (should succeed -> app_id printed)"
dm stop --app-id $APP_ID_1

echo "12. Stopping $APP_ID_2 with short   timeout (should fail -> no print)"
dm stop --app-id $APP_ID_2 --timeout 1

echo "13. Killing  $APP_ID_2"
dm kill --app-id $APP_ID_2