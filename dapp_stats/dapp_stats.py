from collections import defaultdict
import pydantic
from typing import DefaultDict, Dict, Optional

from dapp_manager import DappManager

from .exceptions import DappStatsException
from .statistics.models import NodeStat
from .statistics.schemas import StateLogEntry


class DappStats:
    def __init__(self, app_id: str):
        self._app_id = app_id

    def _iter_app_states(self):
        return DappManager(self._app_id).storage.iter_file("state")

    def get_stats(self) -> Dict:
        nodes_stats: DefaultDict[str, Dict[int, NodeStat]] = defaultdict(dict)
        app_stats: Optional[NodeStat] = None

        for raw_state in self._iter_app_states():
            try:
                app_state = StateLogEntry.parse_raw(raw_state)
            except pydantic.ValidationError:
                raise DappStatsException(
                    f"dApp {self._app_id } state log is corrupted. Unable to generate statistics."
                )

            if app_stats is not None:
                app_stats += NodeStat(
                    state=app_state.app, timestamp=app_state.timestamp
                )
            else:
                app_stats = NodeStat(state=app_state.app, timestamp=app_state.timestamp)

            for node, node_states in app_state.nodes.items():
                for node_idx, state in node_states.items():
                    node_stat = NodeStat(state=state, timestamp=app_state.timestamp)
                    if node_idx in nodes_stats[node]:
                        nodes_stats[node][node_idx] += node_stat
                    else:
                        nodes_stats[node][node_idx] = node_stat

        return {
            "app": app_stats.to_dict() if app_stats is not None else {},
            "nodes": {
                node: {idx: idx_stat.to_dict() for idx, idx_stat in node_stats.items()}
                for node, node_stats in nodes_stats.items()
            },
        }