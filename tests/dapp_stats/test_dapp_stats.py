from datetime import timedelta
from unittest.mock import patch

from dapp_stats import DappStats


def test_get_stats():
    states_payload = [
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
    assert stats["db"][0]["launched successfully"] == True
    assert stats["db"][0]["estimated time to launch"] == timedelta(minutes=2)
    assert stats["http"][0]["launched successfully"] == True
    assert stats["http"][0]["estimated time to launch"] == timedelta(minutes=2)
