from contextlib import contextmanager
import uuid
from typing import List, Union
import os
import signal
from pathlib import Path
from time import sleep

import appdirs
import psutil

from .storage import SimpleStorage
from .dapp_starter import DappStarter

PathType = Union[str, os.PathLike]


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
        self.storage = self._create_storage(app_id)

    @classmethod
    def list(cls) -> List[str]:
        """Return a list of ids of all known apps, sorted by the creation date"""
        return SimpleStorage.app_id_list(cls._get_data_dir())

    @classmethod
    def start(
        cls, descriptor: PathType, *other_descriptors: PathType, config: PathType
    ) -> "DappManager":
        """Start a new app"""
        #   TODO: https://github.com/golemfactory/dapp-manager/issues/7
        descriptor_paths = [Path(d) for d in [descriptor, *other_descriptors]]
        config_path = Path(config)

        app_id = uuid.uuid4().hex
        storage = cls._create_storage(app_id)
        storage.init()

        starter = DappStarter(descriptor_paths, config_path, storage)
        starter.start()

        return cls(app_id)

    @property
    def pid(self) -> int:
        return self.storage.pid

    def raw_state(self) -> str:
        """Return raw, unparsed contents of the 'state' stream"""
        return self.storage.state

    def raw_data(self) -> str:
        """Return raw, unparsed contents of the 'data' stream"""
        return self.storage.data

    def stop(self, timeout: int) -> bool:
        """Stop the dapp gracefully (SIGINT), waiting at most `timeout` seconds.

        Returned value indicates if the app was succesfully stopped."""

        # TODO: https://github.com/golemfactory/dapp-manager/issues/11
        # TODO: Consider refactoring. If we remove "os.waitpid", the whole enforce_timeout thing is
        #       redundant. Related issues:
        #       https://github.com/golemfactory/dapp-manager/issues/9
        #       https://github.com/golemfactory/dapp-manager/issues/10
        with enforce_timeout(timeout):
            os.kill(self.pid, signal.SIGINT)
            self._wait_until_stopped()
            return True
        return False

    def _wait_until_stopped(self) -> None:
        try:
            #   This is how we wait if we started the dapp-runner child process
            #   from the current process.
            os.waitpid(self.pid, 0)
        except ChildProcessError:
            #   And this is how we wait if this is not a child process (e.g. we're using CLI)
            while psutil.pid_exists(self.pid):
                sleep(0.1)

    def kill(self) -> None:
        """Stop the app in a non-gracfeul way"""

        # TODO: https://github.com/golemfactory/dapp-manager/issues/11

        os.kill(self.pid, signal.SIGKILL)

    #   EXTENDED INTERFACE (this part requires further considerations)
    def stdout(self) -> str:
        """Stdout of the dapp-runner"""
        return "This is stdout"

    def stderr(self) -> str:
        """Stderr of the dapp-runner"""
        return "This is stderr"

    def state(self) -> dict:
        """Parsed contents of the 'state' stream"""
        return {"resource_x": "running on provider some-name"}

    def data(self) -> dict:
        """Parsed contents od the 'data' stream"""
        return {"resource_x": {"IP": "127.0.0.1"}}

    @classmethod
    def prune(cls) -> List[str]:
        """Remove all the information about past (i.e. not running now) apps.

        This removes the database entry (if the app was not stopped gracefully) and
        all of the data passed from the dapp-runner (e.g. data, state etc).

        Returns a list of app_ids of the pruned apps."""

    @classmethod
    def _create_storage(cls, app_id: str) -> SimpleStorage:
        return SimpleStorage(app_id, cls._get_data_dir())

    @staticmethod
    def _get_data_dir() -> str:
        return appdirs.user_data_dir("dapp_manager", "golemfactory")


@contextmanager
def enforce_timeout(seconds: int):
    """This context manager exits after `seconds`."""
    # TODO: https://github.com/golemfactory/dapp-manager/issues/10

    def raise_timeout_error(signum, frame):
        raise TimeoutError

    signal.signal(signal.SIGALRM, raise_timeout_error)
    signal.alarm(seconds)

    try:
        yield
    except TimeoutError:
        pass
    finally:
        signal.signal(signal.SIGALRM, signal.SIG_IGN)
