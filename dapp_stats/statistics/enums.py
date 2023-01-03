from enum import Enum


class NodeState(str, Enum):
    pending = "pending"
    starting = "starting"
    running = "running"
    stopping = "stopping"
    terminated = "terminated"
    unresponsive = "unresponsive"
