from datetime import datetime, timedelta

from dapp_stats.statistics import enums, models


def test_accumulated_node_stats_launched_successfully():
    accumulated_node_stats = models.NodeStat()
    now = datetime.now()
    for stamp, state in [
        (now + timedelta(minutes=0), enums.StateEnum.pending),
        (now + timedelta(minutes=1), enums.StateEnum.starting),
        (now + timedelta(minutes=2), enums.StateEnum.running),
    ]:
        accumulated_node_stats += models.NodeStat(stamp=stamp, state=state)
    assert accumulated_node_stats._changes == 3
    assert accumulated_node_stats._launched_successfully == True
    assert accumulated_node_stats._error_on_launch == False
    assert accumulated_node_stats._working_time == timedelta(minutes=2)
    assert accumulated_node_stats._time_to_launch == timedelta(minutes=2)


def test_accumulated_node_stats_error_on_launch():
    accumulated_node_stats = models.NodeStat()
    now = datetime.now()
    for stamp, state in [
        (now + timedelta(minutes=0), enums.StateEnum.pending),
        (now + timedelta(minutes=1), enums.StateEnum.starting),
        (now + timedelta(minutes=2), enums.StateEnum.unresponsive),
    ]:
        accumulated_node_stats += models.NodeStat(stamp=stamp, state=state)
    assert accumulated_node_stats._changes == 3
    assert accumulated_node_stats._launched_successfully == False
    assert accumulated_node_stats._error_on_launch == True
    assert accumulated_node_stats._working_time == timedelta(minutes=2)
    assert accumulated_node_stats._time_to_launch == timedelta()
