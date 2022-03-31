from pathlib import Path
from typing import Optional


class SimpleStorage:
    DEFAULT_BASE_DIR = '_dapp_data'

    def __init__(self, app_id: str, base_dir: str = DEFAULT_BASE_DIR):
        self.app_id = app_id
        self.base_dir = Path(base_dir)

    def save_pid(self, pid: int) -> None:
        self._ensure_data_dir_exists()
        with open(self.pid_file, 'w') as f:
            f.write(str(pid))

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

    def _ensure_data_dir_exists(self) -> None:
        self._data_dir.mkdir(parents=True, exist_ok=True)

    @property
    def _data_dir(self) -> Path:
        return self.base_dir / self.app_id
