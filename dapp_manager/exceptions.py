from typing import Optional


class DappManagerException(Exception):
    """Base exception for all dapp-manager exceptions."""

    SHELL_EXIT_CODE = 3


class UnknownApp(DappManagerException):
    """Exception raised when APP_ID is not found in the database.

    There are two main scenarios for this exception:
    A) APP_ID is invalid
    B) APP_ID references an app that is no longer running and its data was already
    removed by a call to DappManager.prune()
    """

    SHELL_EXIT_CODE = 4

    def __init__(self, app_id):
        super().__init__(f"{app_id} is not an id of any known app")


class AppNotRunning(DappManagerException):
    """Exception raised when the app identified by APP_ID is known, but no longer \
    running.

    We don't know if it was stopped by a stop/kill command, or exited on its own, or
    maybe the process was killed some other way.
    """

    SHELL_EXIT_CODE = 5

    def __init__(self, app_id):
        super().__init__(f"App {app_id} is not running.")


class StartupFailed(DappManagerException):
    """Exception raised when the command `start` fails.

    Or, to be more exact: 1 second after `start` was executed the app process doesn't
    exist.
    """

    SHELL_EXIT_CODE = 6

    def __init__(self, stdout, stderr, runner_stdout: Optional[str], runner_stderr: Optional[str]):
        if runner_stderr is None:
            runner_stderr_text = "--- no dapp-runner stderr ---"
        else:
            runner_stderr_text = f"--- dapp-runner stderr ---\n{runner_stderr}"

        if runner_stdout is None:
            runner_stdout_text = "--- no dapp-runner stdout ---"
        else:
            runner_stdout_text = f"--- dapp-runner stdout ---\n{runner_stdout}"

        msg = "\n".join(
            [
                "Dapp startup failed.",
                runner_stderr_text,
                runner_stdout_text,
                "--- pre-runner stderr ---",
                stderr,
                "--- pre-runner stdout ---",
                stdout,
            ]
        )

        super().__init__(msg)


class GaomApiUnavailable(DappManagerException):
    """Exception raised the command requires the GAOM API to be available but is not present.

    For the API to be available, the `dapp-manager` must be invoked with the `--api` option
    specifying the hostname and port.
    """

    SHELL_EXIT_CODE = 7

    def __init__(self, app_id):
        super().__init__(
            f"GAOM API unavailable for {app_id}. Please start the app with the `--app-port` option."
        )


class AppRunning(DappManagerException):
    """Exception raised when a given app is running but expected to have been stopped.

    We expect the app to be not running (e.g. after having been suspended). We raise the exception
    when it's running in such case.
    """

    SHELL_EXIT_CODE = 8

    def __init__(self, app_id):
        super().__init__(f"App {app_id} is running.")


class NoGaomSaveFile(DappManagerException):
    """Exception raised when no saved GAOM state is available when an app is about to be resumed."""

    SHELL_EXIT_CODE = 9

    def __init__(self, app_id):
        super().__init__(f"No saved GAOM state available for {app_id}.")


class GaomApiError(DappManagerException):
    """General error while accessing the GAOM API."""

    SHELL_EXIT_CODE = 10

    def __init__(self, app_id):
        super().__init__(f"GAOM API error in {app_id}. Check the logs for details")
