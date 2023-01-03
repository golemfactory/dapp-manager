from datetime import datetime
from pydantic import BaseModel
from typing import Dict

from dapp_stats.statistics.enums import NodeState


class StateLogEntry(BaseModel):
    nodes: Dict[str, Dict[int, NodeState]]
    timestamp: datetime
    app: NodeState
