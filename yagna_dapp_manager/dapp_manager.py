from datetime import timedelta
import uuid
from typing import List, Optional, Union
from os import PathLike
from pathlib import Path

from .storage import SimpleStorage
from .dapp_starter import DappStarter

PathType = Union[str, bytes, PathLike]


class DappManager:
    """Manage multiple dapps

    General notes:
    * DappManager instances are stateless -> there is never a difference
      between using a newly created DappManager object and using one created before, as long
      as they share the same app_id
    * All DappMangers running in the same working directory share the same data
    * UnknownApp exception can be thrown out of any instance method
    * There's no problem having multiple DappManager instances at the same time"""

    #   MINIMAL INTERFACE
    def __init__(self, app_id: str):
        self.app_id = app_id
        self.storage = SimpleStorage(app_id)

    @classmethod
    def list(cls) -> List[str]:
        """Return a list of ids of all known apps, sorted by the creation date"""
        return SimpleStorage.app_id_list()

    @classmethod
    def start(cls, descriptor: PathType, *other_descriptors: PathType, config: PathType) -> "DappManager":
        """Start a new app"""
        app_id = uuid.uuid4().hex

        #   TODO: ensure files exist
        descriptor_paths = [Path(d) for d in [descriptor, *other_descriptors]]
        config_path = Path(config)

        starter = DappStarter(descriptor_paths, config_path, SimpleStorage(app_id))
        starter.start()

        return cls(app_id)

    @property
    def pid(self) -> Optional[int]:
        return self.storage.pid

    def raw_status(self) -> str:
        """Return raw, unparsed contents of the 'status' stream"""
        return f"status of the app {self.app_id}"

    def raw_data(self) -> str:
        """Return raw, unparsed contents of the 'data' stream"""
        return f"data of the app {self.app_id}"

    def stop(self, timeout=timedelta(seconds=15)) -> bool:
        """Stop the app gracefully. Returned value indicates if the app was succesfully stopped."""
        return True

    #   EXTENDED INTERFACE (this part requires further considerations)
    def stdout(self) -> str:
        """Stdout of the dapp-runner"""
        return "This is stdout"

    def stderr(self) -> str:
        """Stderr of the dapp-runner"""
        return "This is stderr"

    def status(self) -> dict:
        """Parsed contents of the 'status' stream"""
        return {'resource_x': 'running on provider some-name'}

    def data(self) -> dict:
        """Parsed contents od the 'data' stream"""
        return {'resource_x': {'IP': '127.0.0.1'}}

    def kill(self) -> None:
        """Stop the app in a non-gracfeul way"""

    @classmethod
    def prune(cls) -> List[str]:
        """Remove all the information about past (i.e. not running now) apps.

        This removes the database entry (if the app was not stopped gracefully) and
        all of the data passed from the dapp-runner (e.g. data, status etc).

        Returns a list of app_ids of the pruned apps."""
