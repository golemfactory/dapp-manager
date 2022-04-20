from pathlib import Path
import os

from typing import List


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
    def pid(self) -> int:
        # TODO: https://github.com/golemfactory/dapp-manager/issues/6
        # (this will also influence other methods here)
        with open(self.pid_file, "r") as f:
            return int(f.read())

    @property
    def pid_file(self) -> Path:
        return self._fname("pid")

    @property
    def data_file(self) -> Path:
        return self._fname("data")

    @property
    def state_file(self) -> Path:
        return self._fname("state")

    def _fname(self, name) -> Path:
        return self._data_dir / name

    @property
    def _data_dir(self) -> Path:
        return self.base_dir / self.app_id
