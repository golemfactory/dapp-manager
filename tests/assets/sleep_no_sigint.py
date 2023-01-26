import signal
import sys
import time


# Handling graceful shutdown for windows.
# See https://github.com/golemfactory/dapp-manager/pull/76
def handler(signum, frame):
    pass


signal.signal(signal.SIGBREAK if sys.platform == "win32" else signal.SIGINT, handler)

for _ in range(int(sys.argv[1])):
    time.sleep(1)
