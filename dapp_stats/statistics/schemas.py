from datetime import datetime
from pydantic import BaseModel
from typing import Dict

from dapp_stats.statistics.enums import StateEnum


class StateLog(BaseModel):
    nodes: Dict[str, Dict[int, StateEnum]]
    timestamp: datetime
    app: StateEnum
