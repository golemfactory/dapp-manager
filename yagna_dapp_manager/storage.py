from pathlib import Path
from typing import Optional
import os


class SimpleStorage:
    DEFAULT_BASE_DIR = '_dapp_data'

    def __init__(self, app_id: str):
        self.app_id = app_id
        self.base_dir = Path(self.DEFAULT_BASE_DIR)

    def init(self) -> None:
        """Initialize storage for `self.app_id`

        NOTE: we don't want to do this in __init__ because SimpleStorage doesn't
        know if `self.app_id` makes any sense."""
        self._data_dir.mkdir(parents=True)

    def save_pid(self, pid: int) -> None:
        with open(self.pid_file, 'w') as f:
            f.write(str(pid))

    @property
    def status(self) -> str:
        try:
            with open(self.status_file, 'r') as f:
                return f.read()
        except FileNotFoundError:
            return ''

    @property
    def data(self) -> str:
        try:
            with open(self.data_file, 'r') as f:
                return f.read()
        except FileNotFoundError:
            return ''

    @classmethod
    def app_id_list(cls):
        paths = sorted(Path(cls.DEFAULT_BASE_DIR).iterdir(), key=os.path.getmtime)
        return [path.stem for path in paths]

    @property
    def pid(self) -> Optional[int]:
        try:
            with open(self.pid_file, 'r') as f:
                return int(f.read())
        except FileNotFoundError:
            return None

    @property
    def pid_file(self) -> Path:
        return self._fname('pid')

    @property
    def data_file(self) -> Path:
        return self._fname('data')

    @property
    def status_file(self) -> Path:
        return self._fname('status')

    def _fname(self, name) -> Path:
        return self._data_dir / name

    @property
    def _data_dir(self) -> Path:
        return self.base_dir / self.app_id
