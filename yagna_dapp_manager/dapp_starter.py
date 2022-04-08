from subprocess import Popen, DEVNULL
from typing import List
from pathlib import Path

from .storage import SimpleStorage


class DappStarter:
    def __init__(self, descriptors: List[Path], config: Path, storage: SimpleStorage):
        self.descriptors = descriptors
        self.config = config
        self.storage = storage

    def start(self) -> int:
        command = self._get_command()

        #   NOTE: Stdout and stderr are redirected to /dev/null.
        #         This will probably never change - we assume the dapp runner either has
        #         no meaningfull stdout/stderr, or has an additional interface that allows
        #         redirecting it to a file (just like e.g. --data-file).
        proc = Popen(command, stdout=DEVNULL, stderr=DEVNULL)
        self.storage.save_pid(proc.pid)

    def _get_command(self):
        # TODO: https://github.com/golemfactory/dapp-manager/issues/5
        raise NotImplementedError
