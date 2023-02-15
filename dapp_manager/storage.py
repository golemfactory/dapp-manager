import io
import os
import re
import shutil
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, List, Literal, Optional, Tuple, Union

from .exceptions import UnknownApp

READ_FILE_ITER_CHUNK_SIZE = 1024

RunnerFileType = Literal["data", "state", "log", "stdout", "stderr", "commands"]
RunnerReadFileType = Literal["data", "state", "log", "stdout", "stderr"]


class SimpleStorage:
    def __init__(self, app_id: str, data_dir: str):
        self.app_id = re.sub("[\n\r/\\\\.]", "", app_id)
        self.base_dir = Path(data_dir).resolve()

    def init(self) -> None:
        """Initialize storage for `self.app_id`.

        There is a separate method (instead of e.g. a call in `__init__`) because we want to do
        this only once per `app_id` and in a fully controlled manner.
        """

        self._data_dir.mkdir(parents=True)

    def save_pid(self, pid: int) -> None:
        # TODO: https://github.com/golemfactory/dapp-manager/issues/12
        with open(self.pid_file, "w") as f:
            f.write(str(pid))

    def set_not_running(self) -> None:
        try:
            os.rename(self.pid_file, self.archived_pid_file)
        except FileNotFoundError:
            pass

    def delete(self) -> None:
        try:
            shutil.rmtree(self._data_dir)
        except FileNotFoundError:
            pass

    @property
    def alive(self) -> bool:
        return os.path.isfile(self.pid_file)

    @contextmanager
    def open(self, file_type: RunnerFileType, mode):
        with self.file_name(file_type).open(mode) as f:
            yield f

    def read_file(self, file_type: RunnerFileType) -> str:
        with self.open(file_type, "r") as f:
            return f.read()

    def iter_file_chunks(
        self,
        file_type: RunnerReadFileType,
        *,
        start_pos: Optional[int] = 0,
        chunk_size: Optional[int] = None,
    ) -> Iterator[Tuple[int, str]]:
        """Read chunks of content from given position to end of given stream.

        If read reached end of stream, file handler will be closed.

        Returns tuple of:
         - size of read data
         - data itself
        """

        with self.open(file_type, "r") as f:
            file_size = f.seek(0, io.SEEK_END)
            f.seek(start_pos)
            previous_pos = start_pos

            while True:
                data = f.read(chunk_size)

                if not data:
                    # We have no more data in file, end the iteration
                    return

                current_pos = f.tell()
                read_size = current_pos - previous_pos
                previous_pos = current_pos

                if current_pos == file_size:
                    # We have some data, but we reached to end of file
                    #  so let's leave the loop end file context
                    break

                # yield data but hold log file open
                yield read_size, data

        # yield data but after closing log file
        yield read_size, data

    def iter_file_lines(self, file_type: RunnerReadFileType) -> Iterator[str]:
        try:
            with self.open(file_type, "r") as f:
                for line in f:
                    yield line
        except FileNotFoundError:
            return

    def write_file(self, file_type: RunnerFileType, data: str):
        with self.open(file_type, "a") as f:
            return f.write(data)

    @classmethod
    def app_id_list(cls, data_dir: str) -> List[str]:
        try:
            paths = sorted(Path(data_dir).iterdir(), key=os.path.getmtime)
            return [path.stem for path in paths]
        except FileNotFoundError:
            return []

    @property
    def pid(self) -> int:
        try:
            with open(self.pid_file, "r") as f:
                return int(f.read())
        except FileNotFoundError:
            with open(self.archived_pid_file, "r") as f:
                return int(f.read())

    @property
    def pid_file(self) -> Path:
        return self.file_name("pid")

    @property
    def archived_pid_file(self) -> Path:
        return self.file_name("_old_pid")

    def file_name(self, name: Union[RunnerFileType, Literal["pid", "_old_pid"]]) -> Path:
        # NOTE: "Known app" test here is sufficient - this method will be called whenever any piece
        # of information related to self.app_id is retrieved or changed
        self._ensure_known_app()
        return self._data_dir / name

    def _ensure_known_app(self) -> None:
        if not os.path.isdir(self._data_dir):
            raise UnknownApp(self.app_id)

    @property
    def _data_dir(self) -> Path:
        try:
            (self.base_dir / self.app_id).resolve().relative_to(self.base_dir)
        except ValueError:
            raise UnknownApp(self.app_id)

        return self.base_dir / self.app_id
