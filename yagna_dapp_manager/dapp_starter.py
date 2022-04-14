import os
from subprocess import Popen, DEVNULL
from typing import List
from pathlib import Path

from .storage import SimpleStorage


class DappStarter:
    def __init__(self, descriptors: List[Path], config: Path, storage: SimpleStorage):
        self.descriptors = descriptors
        self.config = config
        self.storage = storage

    def start(self) -> None:
        command = self._get_command()

        #   NOTE: Stdout and stderr are redirected to /dev/null.
        #         This will probably never change - we assume the dapp runner either has
        #         no meaningfull stdout/stderr, or has an additional interface that allows
        #         redirecting it to a file (just like e.g. --data-file).
        proc = Popen(command, stdout=DEVNULL, stderr=DEVNULL)
        self.storage.save_pid(proc.pid)

    def _get_command(self):
        return [self._executable()] + self._cli_args()

    def _cli_args(self) -> List[str]:
        """Return the dapp-runner CLI command and args."""
        # TODO: https://github.com/golemfactory/dapp-manager/issues/5
        args = ["start"]
        args += ["--config", str(self.config.resolve())]
        args += ["--data", str(self.storage.data_file.resolve())]
        args += ["--state", str(self.storage.status_file.resolve())]
        args += [str(d.resolve()) for d in self.descriptors]
        return args

    def _executable(self) -> str:
        """Return the "dapp-runner" executable - either set by the env variable or the default.

        Env variable is intended mostly for the testing/debugging purposes."""
        executable = os.environ["DAPP_RUNNER_EXEC"]
        if not executable:
            # TODO: https://github.com/golemfactory/dapp-manager/issues/5
            raise NotImplementedError
        return executable
