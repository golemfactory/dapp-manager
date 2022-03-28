class UnknownApp(Exception):
    """Exception raised when APP_ID is not found in the database

    i.e. either the APP_ID is invalid, or the app was already succesfully stopped and forgotten."""
    def __init__(self, app_id):
        return super().__init__(f"{app_id} is not an id of any known app")


class AppNotRunning(Exception):
    """Exception raised when APP_ID is a known app id, but the corresponding process does not exist.

    Few possible reasons:
    * The dapp-runner process just finished (e.g. because of an error)
    * The dapp-runner process was stopped not by the DappManager
    * The DappManager database was modified by someone else than the DappManager
    """
    def __init__(self, app_id):
        return super().__init__(f"Process for app {app_id} doesn't exist")
