from datetime import datetime, timedelta

from dapp_stats.statistics import enums, models


def test_accumulated_node_stats_starting():
    now = datetime.now()
    accumulated_node_stats = models.NodeStat(now, enums.NodeState.pending)
    for stamp, state in [
        (now + timedelta(minutes=1), enums.NodeState.starting),
    ]:
        accumulated_node_stats += models.NodeStat(timestamp=stamp, state=state)
    assert accumulated_node_stats._changes == 2
    assert accumulated_node_stats._launched_successfully == False
    assert accumulated_node_stats._time_to_launch == timedelta()
    assert accumulated_node_stats._working_time == timedelta(minutes=1)


def test_accumulated_node_stats_running():
    now = datetime.now()
    accumulated_node_stats = models.NodeStat(now, enums.NodeState.pending)
    for stamp, state in [
        (now + timedelta(minutes=1), enums.NodeState.starting),
        (now + timedelta(minutes=2), enums.NodeState.running),
    ]:
        accumulated_node_stats += models.NodeStat(timestamp=stamp, state=state)
    assert accumulated_node_stats._changes == 3
    assert accumulated_node_stats._launched_successfully == True
    assert accumulated_node_stats._time_to_launch == timedelta(minutes=2)
    assert accumulated_node_stats._working_time == timedelta(minutes=2)


def test_accumulated_node_stats_terminated():
    now = datetime.now()
    accumulated_node_stats = models.NodeStat(now, enums.NodeState.pending)
    for stamp, state in [
        (now + timedelta(minutes=1), enums.NodeState.starting),
        (now + timedelta(minutes=2), enums.NodeState.running),
        (now + timedelta(minutes=3), enums.NodeState.terminated),
    ]:
        accumulated_node_stats += models.NodeStat(timestamp=stamp, state=state)
    assert accumulated_node_stats._changes == 4
    assert accumulated_node_stats._launched_successfully == True
    assert accumulated_node_stats._time_to_launch == timedelta(minutes=2)
    assert accumulated_node_stats._working_time == timedelta(minutes=3)
