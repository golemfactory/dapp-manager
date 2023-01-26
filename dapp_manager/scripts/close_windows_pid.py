import ctypes
import sys

import psutil

kernel = ctypes.windll.kernel32

# def handler(sig, frame):
#     raise KeyboardInterrupt
#
# signal.signal(signal.SIGBREAK, handler)

process = psutil.Process(int(sys.argv[1]))

kernel.AttachConsole(process.pid)
kernel.SetConsoleCtrlHandler(None, 1)
kernel.GenerateConsoleCtrlEvent(0, 0)
process.wait()
kernel.SetConsoleCtrlHandler(None, 0)

sys.exit(0)
