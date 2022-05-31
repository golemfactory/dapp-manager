function dm () {
    python3 -m dapp_manager "$@"
}

echo "1. Current apps"
dm list

echo "What about app 'no_such_app'?"
dm read state no_such_app
echo "Exit code: $?"

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
dm read state $APP_ID_1

echo "7. Print data file for $APP_ID_1"
dm read data $APP_ID_1

sleep 2

echo "8. Print state file for $APP_ID_1"
dm read state $APP_ID_1

echo "9. Print data file for $APP_ID_1"
dm read data $APP_ID_1

echo "10. Print data file for $APP_ID_2"
dm read data $APP_ID_2

echo "11. Stopping $APP_ID_1 with default timeout (should succeed -> app_id printed)"
dm stop $APP_ID_1

echo "12. Stopping $APP_ID_2 with short timeout (should fail -> no print)"
dm stop --timeout 1 $APP_ID_2

echo "13. Killing  $APP_ID_2"
dm kill $APP_ID_2

echo "14. Check read state of $APP_ID_1 without --no-ensure-alive"
dm read state $APP_ID_1
echo "Exit code: $?"

echo "15. Check read state of $APP_ID_1 with --no-ensure-alive"
dm read state --no-ensure-alive $APP_ID_1

echo "16. Check read state of $APP_ID_2 with --no-ensure-alive"
dm read state --no-ensure-alive $APP_ID_2 

echo "17. Check app list again"
dm list

echo "18. Prune dead apps"
dm prune

echo "19. Check the list again"
dm list
