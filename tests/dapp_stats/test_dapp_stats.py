from datetime import timedelta
from typing import List
from unittest.mock import patch

from dapp_stats import DappStats


def test_get_stats_ok():
    states_payload: List[str] = [
        '{"nodes": {"db": {"0": "pending"}}, "timestamp": "2022-12-19T10:22:53Z", "app": "pending"}',
        '{"nodes": {"db": {"0": "starting"}}, "timestamp": "2022-12-19T10:23:53Z", "app": "starting"}',
        '{"nodes": {"db": {"0": "running"}, "http": {"0": "pending"}}, "timestamp": "2022-12-19T10:24:53Z", "app": "starting"}',
        '{"nodes": {"db": {"0": "running"}, "http": {"0": "starting"}}, "timestamp": "2022-12-19T10:25:53Z", "app": "starting"}',
        '{"nodes": {"db": {"0": "running"}, "http": {"0": "running"}}, "timestamp": "2022-12-19T10:26:53Z", "app": "running"}',
    ]
    dapp_stats = DappStats("app_id")
    with patch.object(
        DappStats, DappStats._iter_app_states.__name__, return_value=states_payload
    ) as _:
        stats = dapp_stats.get_stats()
    assert stats["nodes"]["db"][0]["launched_successfully"] == True
    assert stats["nodes"]["db"][0]["estimated_time_to_launch"] == timedelta(minutes=2)
    assert stats["nodes"]["http"][0]["launched_successfully"] == True
    assert stats["nodes"]["http"][0]["estimated_time_to_launch"] == timedelta(minutes=2)
    assert stats["app"]["launched_successfully"] == True
    assert stats["app"]["estimated_time_to_launch"] == timedelta(minutes=4)


def test_get_stats_no_states():
    states_payload: List[str] = []
    dapp_stats = DappStats("app_id")
    with patch.object(
        DappStats, DappStats._iter_app_states.__name__, return_value=states_payload
    ) as _:
        stats = dapp_stats.get_stats()
    assert stats["nodes"] == {}
    assert stats["app"] == {}
