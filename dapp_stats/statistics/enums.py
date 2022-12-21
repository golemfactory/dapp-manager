from enum import Enum


class StateEnum(str, Enum):
    pending = "pending"
    starting = "starting"
    running = "running"
    stopping = "stopping"
    terminated = "terminated"
    unresponsive = "unresponsive"
