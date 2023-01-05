from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Optional

from dapp_stats.statistics.enums import NodeState


@dataclass
class NodeStatistics:
    timestamp: datetime
    state: NodeState
    _changes: int = 1
    _launched_successfully: bool = False
    _terminated: bool = False
    _time_to_launch: Optional[timedelta] = None
    _working_time: Optional[timedelta] = None

    def __add__(self, other):
        time_since_first_stat = other.timestamp - self.timestamp
        if self.state != other.state:
            self.state = other.state
            self._changes += 1
            if self.state == NodeState.running:
                self._launched_successfully = True
                self._time_to_launch = time_since_first_stat
            if self.state == NodeState.terminated:
                self._terminated = True
                self._working_time = time_since_first_stat
        return self

    def to_dict(self) -> Dict:
        return {
            "state_changes": self._changes,
            "launched_successfully": self._launched_successfully,
            "time_to_launch": self._time_to_launch,
            "terminated": self._terminated,
            "working_time": self._working_time,
        }
