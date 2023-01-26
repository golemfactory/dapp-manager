import shutil
import sys
import time

shutil.copyfile("tests/assets/mock_state_file.txt", sys.argv[1])
shutil.copyfile("tests/assets/mock_data_file.txt", sys.argv[2])

# This sleep is to pretend that this app is running for a "while"
# (apps that return immediately require a special approach in tests,
# because of the AppNotRunning exception).
time.sleep(1)
