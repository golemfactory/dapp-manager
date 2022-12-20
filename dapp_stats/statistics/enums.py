from enum import Enum


class StateEnum(str, Enum):
    none = ""
    pending = "pending"
    starting = "starting"
    running = "running"
    stopping = "stopping"
    terminated = "terminated"
    unresponsive = "unresponsive"
