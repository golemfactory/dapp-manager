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

for _ in range(int(sys.argv[1])):
    time.sleep(1)
