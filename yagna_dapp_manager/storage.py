from pathlib import Path
import os

from typing import List, Optional

from .exceptions import UnknownApp


class SimpleStorage:
    def __init__(self, app_id: str, data_dir: str):
        self.app_id = app_id
        self.base_dir = Path(data_dir)

    def init(self) -> None:
        """Initialize storage for `self.app_id`

        There is a separate method (instead of e.g. a call in `__init__`) because we want to
        do this only once per `app_id` and in a fully controlled manner."""
        self._data_dir.mkdir(parents=True)

    def save_pid(self, pid: int) -> None:
        # TODO: https://github.com/golemfactory/dapp-manager/issues/12
        with open(self.pid_file, "w") as f:
            f.write(str(pid))

    def clear_pid(self) -> None:
        try:
            os.rename(self.pid_file, self.archived_pid_file)
        except FileNotFoundError:
            pass

    @property
    def state(self) -> str:
        try:
            with open(self.state_file, "r") as f:
                return f.read()
        except FileNotFoundError:
            return ""

    @property
    def data(self) -> str:
        try:
            with open(self.data_file, "r") as f:
                return f.read()
        except FileNotFoundError:
            return ""

    @classmethod
    def app_id_list(cls, data_dir: str) -> List[str]:
        try:
            paths = sorted(Path(data_dir).iterdir(), key=os.path.getmtime)
            return [path.stem for path in paths]
        except FileNotFoundError:
            return []

    @property
    def pid(self) -> Optional[int]:
        try:
            with open(self.pid_file, "r") as f:
                return int(f.read())
        except FileNotFoundError:
            # This is a known app that is no longer running
            # (or for some weird reason never got a pid)
            #
            # Invalid  App ID case is a TODO: https://github.com/golemfactory/dapp-manager/issues/6
            # (this will also influence other methods here)
            return None

    @property
    def pid_file(self) -> Path:
        return self._fname("pid")

    @property
    def archived_pid_file(self) -> Path:
        #   TODO: there's currently no way to access this in the API.
        #   BUT: we should first do #13.
        return self._fname("_old_pid")

    @property
    def data_file(self) -> Path:
        return self._fname("data")

    @property
    def state_file(self) -> Path:
        return self._fname("state")

    def _fname(self, name) -> Path:
        #   NOTE: "Known app" test here is sufficient - this method will be called whenever
        #         any piece of information related to self.app_id is retrieved or changed
        self._ensure_known_app()
        return self._data_dir / name

    def _ensure_known_app(self) -> None:
        if not os.path.isdir(self._data_dir):
            raise UnknownApp(self.app_id)

    @property
    def _data_dir(self) -> Path:
        return self.base_dir / self.app_id
