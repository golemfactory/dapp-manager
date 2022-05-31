class DappManagerException(Exception):
    """Base exception for all dapp-manager exceptions"""

    SHELL_EXIT_CODE = 3


class UnknownApp(DappManagerException):
    """Exception raised when APP_ID is not found in the database

    There are two main scenarios for this exception:
    A) APP_ID is invalid
    B) APP_ID references an app that is no longer running and its data was already
       removed by a call to DappManager.prune()"""

    SHELL_EXIT_CODE = 4

    def __init__(self, app_id):
        return super().__init__(f"{app_id} is not an id of any known app")


class AppNotRunning(DappManagerException):
    """Exception raised when the app identified by APP_ID is known, but no longer running.

    We don't know if it was stopped by a stop/kill command, or exited on its own, or maybe
    the process was killed some other way."""

    SHELL_EXIT_CODE = 5

    def __init__(self, app_id):
        return super().__init__(f"App {app_id} is not running.")


class StartupFailed(DappManagerException):
    """Exception raised when the command `start` fails.

    Or, to be more exact: 1 second after `start` was executed the app process doesn't exist."""

    SHELL_EXIT_CODE = 6

    def __init__(self, stdout, stderr, runner_stdout, runner_stderr):
        msg = (
            "Dapp startup failed.\n"
            "--- dapp-runner stderr ---\n"
            f"{runner_stderr}\n\n"
            "--- dapp-runner stdout ---\n"
            f"{runner_stdout}\n\n"
            "--- pre-runner stderr ---\n"
            f"{stderr}\n\n"
            "--- pre-runner stdout ---\n"
            f"{runner_stdout}\n\n"
        )

        return super().__init__(msg)
