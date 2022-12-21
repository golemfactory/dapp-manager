from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict

from dapp_stats.statistics.enums import StateEnum


@dataclass
class NodeStat:
    stamp: datetime
    state: StateEnum
    _changes: int = 1
    _launched_successfully: bool = False
    _working_time: timedelta = field(default_factory=timedelta)
    _time_to_launch: timedelta = field(default_factory=timedelta)

    def __add__(self, other):
        self._working_time = other.stamp - self.stamp
        if self.state != other.state:
            self.state = other.state
            self._changes += 1
            if self.state == StateEnum.running:
                self._launched_successfully = True
                self._time_to_launch = self._working_time
        return self

    def to_dict(self) -> Dict:
        return {
            "state changes": self._changes,
            "launched successfully": self._launched_successfully,
            "estimated time to launch": self._time_to_launch,
            "estimated working time": self._working_time,
            "image size": "Unknown",
        }
