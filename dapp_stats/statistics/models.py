from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict

from dapp_stats.statistics.enums import StateEnum


@dataclass
class NodeStat:
    stamp: datetime = datetime(1, 1, 1)
    state: str = StateEnum.none
    _changes: int = 0
    _launched_successfully: bool = False
    _error_on_launch: bool = False
    _working_time: timedelta = field(default_factory=timedelta)
    _time_to_launch: timedelta = field(default_factory=timedelta)

    def __add__(self, other):
        if self.stamp == datetime(1, 1, 1):
            self.stamp = other.stamp
        self._working_time = other.stamp - self.stamp
        if self.state != other.state:
            self.state = other.state
            self._changes += 1
            if self.state == StateEnum.running:
                self._launched_successfully = True
                self._time_to_launch = self._working_time
            elif self.state in (StateEnum.terminated, StateEnum.unresponsive):
                self._error_on_launch = True
        return self

    def to_dict(self) -> Dict:
        return {
            "state changes": self._changes,
            "launched successfully": self._launched_successfully,
            "error on launch": self._error_on_launch,
            "estimated working time": self._working_time,
            "estimated time to launch": self._time_to_launch,
            "image size": "Unknown",
        }
