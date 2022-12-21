from collections import defaultdict
from typing import DefaultDict, Dict

from dapp_manager import DappManager

from .statistics.models import NodeStat
from .statistics.schemas import State


class DappStats:
    def __init__(self, app_id: str):
        self._app_id = app_id

    def _iter_app_states(self):
        return DappManager(self._app_id).storage.iter_file("state")

    def get_stats(self) -> Dict:
        nodes_stats: DefaultDict[str, Dict[int, NodeStat]] = defaultdict(dict)
        app_stats = ...  # TODO
        for raw_state in self._iter_app_states():
            app_state = State.parse_raw(raw_state)
            for node, node_states in app_state.nodes.items():
                for node_idx, state in node_states.items():
                    node_stat = NodeStat(state=state, stamp=app_state.timestamp)
                    if node_idx in nodes_stats[node]:
                        nodes_stats[node][node_idx] += node_stat
                    else:
                        nodes_stats[node][node_idx] = node_stat

        return {
            node: {idx: idx_stat.to_dict() for idx, idx_stat in node_stats.items()}
            for node, node_stats in nodes_stats.items()
        }
