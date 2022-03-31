from pathlib import Path


class SimpleStorage:
    DEFAULT_BASE_DIR = '_dapp_data'

    def __init__(self, app_id: str, base_dir: str = DEFAULT_BASE_DIR):
        self.app_id = app_id
        self.base_dir = Path(base_dir)

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
        return self.base_dir / self.app_id / name
