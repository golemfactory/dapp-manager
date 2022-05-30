import os
from subprocess import Popen, PIPE
from time import sleep
from typing import List, Tuple
from pathlib import Path

from .storage import SimpleStorage, RunnerFileType

DEFAULT_EXEC_STR = "python3 -m dapp_runner"


class DappStarter:
    def __init__(self, descriptors: List[Path], config: Path, storage: SimpleStorage):
        self.descriptors = descriptors
        self.config = config
        self.storage = storage

    def start(self, timeout: float) -> Tuple[int, str, str]:
        """Start a dapp. Wait TIMEOUT seconds. Return pid, stdout, stderr"""
        command = self._get_command()

        #   NOTE: Stdout/stderr here should not be confused with --stdout and --stderr
        #         passed as arguments to the dapp-runner command.
        #         PIPE captures only the output that was *not* redirected by the dapp-runner,
        #         i.e. python errors (--> stderr/stdout that happened before the dapp-runner started,
        #         or related to internal errors in the dapp-runner).
        proc = Popen(command, stdout=PIPE, stderr=PIPE)

        sleep(timeout)

        output, error_output = [msg.decode() for msg in proc.communicate()]

        return proc.pid, output, error_output

    def _get_command(self):
        return self._executable() + self._cli_args()

    def _cli_args(self) -> List[str]:
        """Return the dapp-runner CLI command and args."""
        # TODO: https://github.com/golemfactory/dapp-manager/issues/5
        args = ["start"]
        args += ["--config", str(self.config.resolve())]

        # TODO: is there's a better way to iterate over elements of a Literal type?
        for file_type in RunnerFileType.__args__:  # type: ignore [attr-defined]
            file_name = str(self.storage.file_name(file_type).resolve())
            args += [f"--{file_type}", file_name]

        args += [str(d.resolve()) for d in self.descriptors]
        return args

    def _executable(self) -> List[str]:
        """Return the "dapp-runner" executable - either set by the env variable or the default.

        Env variable is intended mostly for the testing/debugging purposes."""
        executable_str = os.environ.get("DAPP_RUNNER_EXEC", DEFAULT_EXEC_STR)
        return list(executable_str.split())
