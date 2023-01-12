from enum import Enum

from yapapi.services import ServiceState


class NodeState(str, Enum):
    pending = ServiceState.pending.value
    starting = ServiceState.starting.value
    running = ServiceState.running.value
    stopping = ServiceState.stopping.value
    terminated = ServiceState.terminated.value
    unresponsive = ServiceState.unresponsive.value
