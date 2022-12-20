from ast import Dict
from collections import defaultdict
import json
from typing import DefaultDict

from dapp_manager import DappManager

from .statistics.models import NodeStat
from .statistics.schemas import State


class DappStats:
    def __init__(self, app_id: str):
        self._app_id = app_id
        self._dapp_manager = DappManager(app_id)

    def _iter_app_states(self):
        return self._dapp_manager.storage.iter_file("state")

    def get_stats(self) -> str:
        nodes_stats: DefaultDict[str, DefaultDict[int, NodeStat]] = defaultdict(
            lambda: defaultdict(NodeStat)
        )
        app_stats = ...  # TODO
        for raw_state in self._iter_app_states():
            app_state = State.parse_raw(raw_state)
            for node, node_states in app_state.nodes.items():
                for node_idx, state in node_states.items():
                    nodes_stats[node][node_idx] += NodeStat(
                        state=state, stamp=app_state.timestamp
                    )
        return json.dumps(
            {
                node: {idx: idx_stat.to_dict() for idx, idx_stat in node_stats.items()}
                for node, node_stats in nodes_stats.items()
            },
            indent=4,
            default=str,
        )
