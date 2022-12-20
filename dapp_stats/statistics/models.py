from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional


class State(str, Enum):
    none = ""
    pending = "pending"
    starting = "starting"
    running = "running"
    stopping = "stopping"
    terminated = "terminated"
    unresponsive = "unresponsive"


@dataclass
class Stat:
    stamp: datetime = datetime(1, 1, 1)
    state: str = State.none
    _changes: int = 0
    _launch_count: int = 0
    _successful_launch_count: int = 0
    _unsuccessful_launch_count: int = 0
    _working_time: timedelta = field(default_factory=timedelta)
    _time_to_launch: timedelta = field(default_factory=timedelta)

    def __add__(self, other):
        self._working_time += other.stamp - self.stamp
        if self.state != other.state:
            self.state = other.state
            self._changes += 1
            if self.state == State.pending:
                self._launch_count += 1
            elif self.state == State.running:
                self._successful_launch_count += 1
                self._time_to_launch = self._working_time
            elif self.state in (State.terminated, State.unresponsive):
                self._unsuccessful_launch_count += 1
        return self

    def summary(self):  # TODO type: str or dict
        return f"state changes: {self._changes}, launch count: {self._launch_count}, successful launch count: {self._successful_launch_count}, estimated working time: {self._time_to_launch}, estimated time to launch: {self._time_to_launch}, image size: Unknown"
