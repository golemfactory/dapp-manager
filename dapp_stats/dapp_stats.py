from collections import defaultdict
from typing import DefaultDict, Dict, Optional

import pydantic

from dapp_manager import DappManager

from .exceptions import DappStatsException
from .statistics.models import NodeStatistics
from .statistics.schemas import StateLogEntry


class DappStats:
    def __init__(self, app_id: str):
        self._app_id = app_id

    def _iter_app_states(self):
        return DappManager(self._app_id).storage.iter_file_lines("state")

    def get_stats(self) -> Dict:
        nodes_stats: DefaultDict[str, Dict[int, NodeStatistics]] = defaultdict(dict)
        app_statistics: Optional[NodeStatistics] = None

        for raw_state in self._iter_app_states():
            try:
                app_state = StateLogEntry.parse_raw(raw_state)
            except pydantic.ValidationError:
                raise DappStatsException(
                    f"dApp {self._app_id } state log is corrupted. Unable to generate statistics."
                )

            if app_statistics is not None:
                app_statistics += NodeStatistics(state=app_state.app, timestamp=app_state.timestamp)
            else:
                app_statistics = NodeStatistics(state=app_state.app, timestamp=app_state.timestamp)

            for node, node_states in app_state.nodes.items():
                for node_idx, state in node_states.items():
                    node_stat = NodeStatistics(state=state, timestamp=app_state.timestamp)
                    if node_idx in nodes_stats[node]:
                        nodes_stats[node][node_idx] += node_stat
                    else:
                        nodes_stats[node][node_idx] = node_stat

        return {
            "app": app_statistics.to_dict() if app_statistics is not None else {},
            "nodes": {
                node: {idx: idx_stat.to_dict() for idx, idx_stat in node_stats.items()}
                for node, node_stats in nodes_stats.items()
            },
        }
