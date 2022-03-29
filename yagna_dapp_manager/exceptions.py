class UnknownApp(Exception):
    """Exception raised when APP_ID is not found in the database

    There are two main scenarios for this exception:
    A) APP_ID is invalid
    B) APP_ID references an app that is no longer running and its data was already
       removed by a call to DappManager.prune()"""
    def __init__(self, app_id):
        return super().__init__(f"{app_id} is not an id of any known app")
