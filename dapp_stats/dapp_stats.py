from ast import Dict
from collections import defaultdict
import json
from statistics.models import Stat
from typing import DefaultDict

from dapp_manager import DappManager


class DappStats:
    def __init__(self, app_id: str):
        self._app_id = app_id
        self._dapp_manager = DappManager(app_id)

    def get_stats(self) -> str:
        stats: DefaultDict[str, DefaultDict[str, Stat]] = defaultdict(
            lambda: defaultdict(Stat)
        )
        for raw_state in self._dapp_manager.storage.iter_file(
            "state"
        ):  # TODO make func to hide manager
            app_state = json.loads(raw_state)  # TODO move to external testable func
            for service, service_states in app_state.items():
                for idx, state in service_states.items():
                    stats[service][idx] += Stat(state=state)
        return json.dumps(
            {k: {kk: vv.summary() for kk, vv in v.items()} for k, v in stats.items()},
            indent=4,
        )
