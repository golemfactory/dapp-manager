import time

# This sleep is to pretend that this app is running constantly which require explicit run state
# management in tests
while True:
    time.sleep(1)
