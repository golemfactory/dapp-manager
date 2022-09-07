from contextlib import contextmanager
import uuid
from typing import List, Union
import os
import signal
from pathlib import Path
from time import sleep

import appdirs
import psutil

from .exceptions import AppNotRunning
from .storage import SimpleStorage, RunnerFileType
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

    def __init__(self, app_id: str):
        self.app_id = app_id
        self.storage = self._create_storage(app_id)

    ########################
    #   PUBLIC CLASS METHODS
    @classmethod
    def list(cls) -> List[str]:
        """Return a list of ids of all known apps, sorted by the creation date"""
        return SimpleStorage.app_id_list(cls._get_data_dir())

    @classmethod
    def start(
        cls,
        descriptor: PathType,
        *other_descriptors: PathType,
        config: PathType,
        timeout: float = 1,
    ) -> "DappManager":
        """Start a new app"""
        #   TODO: https://github.com/golemfactory/dapp-manager/issues/7
        descriptor_paths = [Path(d) for d in [descriptor, *other_descriptors]]
        config_path = Path(config)

        app_id = uuid.uuid4().hex
        storage = cls._create_storage(app_id)
        storage.init()

        starter = DappStarter(descriptor_paths, config_path, storage)
        starter.start(timeout=timeout)

        return cls(app_id)

    @classmethod
    def prune(cls) -> List[str]:
        """Remove all the information about past (i.e. not running now) apps.

        This removes the database entry (if the app was not stopped gracefully) and
        all of the data passed from the dapp-runner (e.g. data, state etc).

        Returns a list of app_ids of the pruned apps."""

        pruned = []
        for app_id in cls.list():
            storage = cls._create_storage(app_id)
            if not storage.alive:
                storage.delete()
                pruned.append(app_id)
        return pruned

    ###########################
    #   PUBLIC INSTANCE METHODS
    def read_file(self, file_type: RunnerFileType, ensure_alive: bool = True) -> str:
        """Return raw, unparsed contents of the `file_type` stream.

        If ensure_alive is True, AppNotRunning exception will be raised if the app is not running."""

        if ensure_alive:
            self._ensure_alive()
        return self.storage.read_file(file_type)

    def stop(self, timeout: int) -> bool:
        """Stop the dapp gracefully (SIGINT), waiting at most `timeout` seconds.

        Returned value indicates if the app was succesfully stopped."""
        self._ensure_alive()

        # TODO: Consider refactoring. If we remove "os.waitpid", the whole enforce_timeout thing is
        #       redundant. Related issues:
        #       https://github.com/golemfactory/dapp-manager/issues/9
        #       https://github.com/golemfactory/dapp-manager/issues/10
        with enforce_timeout(timeout):
            os.kill(self.pid, signal.SIGINT)
            self._wait_until_stopped()
            self.storage.set_not_running()
            return True
        return False

    def kill(self) -> None:
        """Stop the app in a non-gracfeul way"""
        self._ensure_alive()

        os.kill(self.pid, signal.SIGKILL)
        self.storage.set_not_running()

    #######################
    #   SEMI-PUBLIC METHODS
    #   (they can be useful when using the API, but are also important parts of the internal logic)
    @property
    def alive(self) -> bool:
        """Check if the app is running now"""
        if not self.storage.alive:
            return False
        self._update_alive()
        return self.storage.alive

    @property
    def pid(self) -> int:
        return self.storage.pid

    ############
    #   HELPERS
    def _wait_until_stopped(self) -> None:
        try:
            #   This is how we wait if we started the dapp-runner child process
            #   from the current process.
            os.waitpid(self.pid, 0)
        except ChildProcessError:
            #   And this is how we wait if this is not a child process (e.g. we're using CLI)
            while psutil.pid_exists(self.pid):
                sleep(0.1)

    def _update_alive(self) -> None:
        if not self._is_running():
            self.storage.set_not_running()

    def _ensure_alive(self) -> None:
        if not self.alive:
            raise AppNotRunning(self.app_id)

    def _is_running(self) -> bool:
        try:
            #   TODO: https://github.com/golemfactory/dapp-manager/issues/9

            this_process = psutil.Process()
            app_process = psutil.Process(self.pid)

            with app_process.oneshot():
                # after we grab the process info, we ensure that:
                # 1. this is our process
                # 2. it's still running
                # 3. the pid has not been reused
                return (
                    this_process.username() == app_process.username()
                    and app_process.status() != psutil.STATUS_ZOMBIE
                    and app_process.create_time()
                    < self.storage.pid_file.stat().st_ctime
                )
        except (psutil.NoSuchProcess, psutil.AccessDenied, FileNotFoundError):
            return False

    ####################
    #   STATIC UTILITIES
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
