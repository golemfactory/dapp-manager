import shutil
import sys
import time

shutil.copyfile("tests/assets/mock_state_file.txt", sys.argv[1])
shutil.copyfile("tests/assets/mock_data_file.txt", sys.argv[2])

# This sleep is to pretend that this app is running constantly which require explicit run state
# management in tests
while True:
    time.sleep(1)
