from datetime import datetime
from typing import Dict

from pydantic import BaseModel

from dapp_stats.statistics.enums import NodeState


class StateLogEntry(BaseModel):
    nodes: Dict[str, Dict[int, NodeState]]
    timestamp: datetime
    app: NodeState
