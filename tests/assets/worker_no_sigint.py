import signal
import sys
import time


# Handling graceful shutdown for windows.
# See https://github.com/golemfactory/dapp-manager/pull/76
def handler(signum, frame):
    pass


if sys.platform == "win32":
    signum = signal.SIGBREAK
else:
    signum = signal.SIGINT

signal.signal(signum, handler)

# This sleep is to pretend that this app is running constantly which require explicit run state
# management in tests
while True:
    time.sleep(1)
