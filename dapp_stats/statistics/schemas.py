from datetime import datetime
from pydantic import BaseModel
from typing import Dict

from dapp_stats.statistics.enums import StateEnum


class State(BaseModel):  # TODO rename maybe
    nodes: Dict[str, Dict[int, StateEnum]]
    timestamp: datetime
    app: str
