from datetime import datetime, timedelta

from dapp_stats.statistics import enums, models


def test_accumulated_node_stats_starting():
    now = datetime.now()
    accumulated_node_stats = models.NodeStat(now, enums.StateEnum.pending)
    for stamp, state in [
        (now + timedelta(minutes=1), enums.StateEnum.starting),
    ]:
        accumulated_node_stats += models.NodeStat(stamp=stamp, state=state)
    assert accumulated_node_stats._changes == 2
    assert accumulated_node_stats._launched_successfully == False
    assert accumulated_node_stats._time_to_launch == timedelta()
    assert accumulated_node_stats._working_time == timedelta(minutes=1)


def test_accumulated_node_stats_running():
    now = datetime.now()
    accumulated_node_stats = models.NodeStat(now, enums.StateEnum.pending)
    for stamp, state in [
        (now + timedelta(minutes=1), enums.StateEnum.starting),
        (now + timedelta(minutes=2), enums.StateEnum.running),
    ]:
        accumulated_node_stats += models.NodeStat(stamp=stamp, state=state)
    assert accumulated_node_stats._changes == 3
    assert accumulated_node_stats._launched_successfully == True
    assert accumulated_node_stats._time_to_launch == timedelta(minutes=2)
    assert accumulated_node_stats._working_time == timedelta(minutes=2)


def test_accumulated_node_stats_terminated():
    now = datetime.now()
    accumulated_node_stats = models.NodeStat(now, enums.StateEnum.pending)
    for stamp, state in [
        (now + timedelta(minutes=1), enums.StateEnum.starting),
        (now + timedelta(minutes=2), enums.StateEnum.running),
        (now + timedelta(minutes=3), enums.StateEnum.terminated),
    ]:
        accumulated_node_stats += models.NodeStat(stamp=stamp, state=state)
    assert accumulated_node_stats._changes == 4
    assert accumulated_node_stats._launched_successfully == True
    assert accumulated_node_stats._time_to_launch == timedelta(minutes=2)
    assert accumulated_node_stats._working_time == timedelta(minutes=3)
