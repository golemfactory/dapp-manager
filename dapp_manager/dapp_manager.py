import json
import os
import re
import signal
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from time import sleep
from typing import Iterator, List, Optional, Union

import appdirs
import psutil

from .dapp_starter import DappStarter
from .exceptions import AppNotRunning
from .storage import RunnerReadFileType, SimpleStorage

PathType = Union[str, os.PathLike]

COMMAND_OUTPUT_INTERVAL = timedelta(seconds=1)
READ_FILE_FOLLOW_INTERVAL = timedelta(milliseconds=100)
READ_FILE_CHUNK_SIZE = 1024


class DappManager:
    """Manage multiple dapps.

    General notes:
    * DappManager instances are stateless -> there is never a difference
      between using a newly created DappManager object and using one created before,
      as long as they share the same app_id
    * All DappMangers running in the same working directory share the same data
    * UnknownApp exception can be thrown out of any instance method
    * There's no problem having multiple DappManager instances at the same time
    """

    def __init__(self, app_id: str):
        self.app_id = app_id
        self.storage = self._create_storage(app_id)

    ########################
    #   PUBLIC CLASS METHODS
    @classmethod
    def list(cls) -> List[str]:
        """Return a list of ids of all known apps, sorted by the creation date."""

        return SimpleStorage.app_id_list(cls._get_data_dir())

    @classmethod
    def start(
        cls,
        descriptor: PathType,
        *other_descriptors: PathType,
        config: PathType,
        log_level: Optional[str] = None,
        timeout: float = 1,
    ) -> "DappManager":
        """Start a new app."""

        descriptor_paths = [Path(d) for d in [descriptor, *other_descriptors]]
        config_path = Path(config)

        app_id = uuid.uuid4().hex
        storage = cls._create_storage(app_id)
        storage.init()

        starter = DappStarter(descriptor_paths, config_path, storage, log_level=log_level)
        starter.start(timeout=timeout)

        return cls(app_id)

    @classmethod
    def prune(cls) -> List[str]:
        """Remove all the information about past (i.e. not running now) apps.

        This removes the database entry (if the app was not stopped gracefully) and
        all of the data passed from the dapp-runner (e.g. data, state etc).

        Returns a list of app_ids of the pruned apps.
        """

        pruned = []
        for app_id in cls.list():
            storage = cls._create_storage(app_id)
            if not storage.alive:
                storage.delete()
                pruned.append(app_id)
        return pruned

    ###########################
    #   PUBLIC INSTANCE METHODS
    def read_file(self, file_type: RunnerReadFileType, *, ensure_alive: bool = True) -> str:
        """Yield raw, unparsed contents of the `file_type` stream.

        If ensure_alive is True, AppNotRunning exception will be raised if the app is
        not running.

        FileNotFoundError exception will be raised if stream is inaccessible (for e.g. deleted).
        """

        if ensure_alive:
            self._ensure_alive()

        return self.storage.read_file(file_type)

    def read_file_follow(
        self, file_type: RunnerReadFileType, *, ensure_alive: bool = True
    ) -> Iterator[str]:
        """Continuously try to yield raw, unparsed contents of the `file_type` stream.

        If ensure_alive is True, AppNotRunning exception will be raised if the app is
        initially not running. If app die and its stream would be inaccessible (for e.g. deleted)
        while following its stream, yielding will end gracefully.

        FileNotFoundError exception will be raised if stream is initially inaccessible
        (for e.g. deleted).
        """

        file_pos = 0
        is_initial_check = True

        while True:
            if ensure_alive:
                try:
                    self._ensure_alive()
                except AppNotRunning:
                    if is_initial_check:
                        raise
                    return

            try:
                for read_size, data in self.storage.iter_file_chunks(
                    file_type, start_pos=file_pos, chunk_size=READ_FILE_CHUNK_SIZE
                ):
                    file_pos += read_size
                    yield data

            except FileNotFoundError:
                if is_initial_check:
                    raise
                return

            # If we managed to get here, special behaviour for initial checks are no longer needed
            is_initial_check = False

            # We've read to end of stream, lets wait a bit and try again
            sleep(READ_FILE_FOLLOW_INTERVAL.total_seconds())

    @staticmethod
    def __parse_service_str(service: str):
        m = re.match("^(?P<service_name>.*?)(\\[(?P<idx>\\d+)\\])?$", service)
        if not m:
            raise ValueError("`service` parameter format unknown, use ")
        service_name = m.group("service_name")
        service_idx = int(m.group("idx") or 0)
        return service_name, service_idx

    @staticmethod
    def __print_executed_command(commands_dict: dict):
        print(commands_dict.get("command"))
        print("success: ", commands_dict.get("success"), "\n")
        print(commands_dict.get("stdout"))
        stderr = commands_dict.get("stderr")
        if stderr:
            print("\nstderr:")
            print(stderr)

    def exec_command(self, service: str, command: List[str], timeout: int):
        self._ensure_alive()

        service_name, service_idx = self.__parse_service_str(service)

        start = datetime.now()
        with self.storage.open("data", "r") as data:
            data.seek(0, 2)

            # send the message to the `commands` stream
            command_msg = json.dumps({service_name: {service_idx: command}})
            self.storage.write_file("commands", command_msg)

            # and wait for the update of the `data` stream
            while datetime.now() < start + timedelta(seconds=timeout):
                data_out = data.readline()
                if not data_out:
                    sleep(COMMAND_OUTPUT_INTERVAL.total_seconds())
                    continue

                msg = json.loads(data_out)

                if isinstance(msg, dict):
                    commands = msg.get(service_name, {}).get(str(service_idx))
                    for cdict in commands:
                        self.__print_executed_command(cdict)
                    break

                raise TimeoutError()

    def stop(self, timeout: int) -> bool:
        """Stop the dapp gracefully (SIGINT), waiting at most `timeout` seconds.

        Returned value indicates if the app was successfully stopped.
        """

        self._ensure_alive()

        process = psutil.Process(self.pid)

        if sys.platform == "win32":
            process.send_signal(signal.CTRL_BREAK_EVENT)
        else:
            process.send_signal(signal.SIGINT)

        try:
            process.wait(timeout)
        except psutil.TimeoutExpired:
            return False

        self.storage.set_not_running()

        return True

    def kill(self) -> None:
        """Stop the app in a non-graceful way."""

        self._ensure_alive()

        process = psutil.Process(self.pid)

        process.kill()

        self.storage.set_not_running()

    #######################
    #   SEMI-PUBLIC METHODS
    #   (they can be useful when using the API, but are also important parts of the
    #   internal logic)
    @property
    def alive(self) -> bool:
        """Check if the app is running now."""

        if not self.storage.alive:
            return False
        self._update_alive()
        return self.storage.alive

    @property
    def pid(self) -> int:
        return self.storage.pid

    ############
    #   HELPERS
    def _update_alive(self) -> None:
        if not self._is_running():
            self.storage.set_not_running()

    def _ensure_alive(self) -> None:
        if not self.alive:
            raise AppNotRunning(self.app_id)

    def _is_running(self) -> bool:
        try:
            # TODO: https://github.com/golemfactory/dapp-manager/issues/9

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
                    and app_process.create_time() < self.storage.pid_file.stat().st_ctime
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
