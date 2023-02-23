import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .exceptions import StartupFailed
from .storage import RunnerFileType, SimpleStorage

DEFAULT_EXEC_STR = "dapp-runner"


class DappStarter:
    def __init__(
        self,
        descriptors: List[Path],
        config: Path,
        storage: SimpleStorage,
        log_level: Optional[str] = None,
    ):
        self.descriptors = descriptors
        self.config = config
        self.storage = storage
        self.log_level = log_level

    def start(self, timeout: float) -> None:
        """Start a dapp. Wait TIMEOUT seconds. Raise StartupFailed if process is not running."""

        command = self._get_command()

        # Handling graceful shutdown for windows.
        # See https://github.com/golemfactory/dapp-manager/pull/76
        kwargs: Dict[str, Any] = {}
        if sys.platform == "win32":
            kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP

        # NOTE: Stdout/stderr here should not be confused with --stdout and --stderr passed as
        #  arguments to the dapp-runner command. PIPE captures only the output that was *not*
        #  redirected by the dapp-runner, i.e. python errors (--> stderr/stdout that happened
        #  before the dapp-runner started, or related to internal errors in the dapp-runner).
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)

        success, stdout, stderr = self._check_succesful_startup(proc, timeout)
        if not success:
            try:
                runner_stdout = self.storage.read_file("stdout")
            except FileNotFoundError:
                runner_stdout = None

            try:
                runner_stderr = self.storage.read_file("stderr")
            except FileNotFoundError:
                runner_stderr = None

            self.storage.delete()

            raise StartupFailed(stdout, stderr, runner_stdout, runner_stderr)

        self.storage.save_pid(proc.pid)

    def _check_succesful_startup(
        self, proc: subprocess.Popen, timeout: float
    ) -> Tuple[bool, str, str]:
        stop = datetime.now() + timedelta(seconds=timeout)

        outputs: List[str] = []
        error_outputs: List[str] = []
        success = True

        while datetime.now() < stop:
            remaining_seconds = (stop - datetime.now()).total_seconds()
            try:
                output, error_output = proc.communicate(timeout=remaining_seconds)
                outputs.append(output.decode())
                error_outputs.append(error_output.decode())
            except subprocess.TimeoutExpired:
                pass

            if proc.poll() is not None:
                success = False
                break

        return success, "\n".join(outputs), "\n".join(error_outputs)

    def _get_command(self):
        return self._executable() + self._cli_args()

    def _cli_args(self) -> List[str]:
        """Return the dapp-runner CLI command and args."""

        # TODO: https://github.com/golemfactory/dapp-manager/issues/5
        args = ["start"]
        args += ["--config", str(self.config.resolve())]

        if self.log_level:
            args += ["--log-level", self.log_level]

        # TODO: is there's a better way to iterate over elements of a Literal type?
        for file_type in RunnerFileType.__args__:  # type: ignore [attr-defined]
            file_name = str(self.storage.file_name(file_type).resolve())
            args += [f"--{file_type}", file_name]

        args += [str(d.resolve()) for d in self.descriptors]
        return args

    def _executable(self) -> List[str]:
        """Return the "dapp-runner" executable - either set by the env variable or the default.

        Env variable is intended mostly for the testing/debugging purposes.
        """

        executable_str = os.environ.get("DAPP_RUNNER_EXEC", DEFAULT_EXEC_STR)
        return list(executable_str.split())
