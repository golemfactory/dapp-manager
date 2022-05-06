"""A bunch of E2E tests of the DappManager interface"""
import psutil
import pytest
from time import sleep

from yagna_dapp_manager import DappManager
from yagna_dapp_manager.exceptions import UnknownApp, AppNotRunning

from .helpers import (
    start_dapp,
    process_is_running,
    get_dapp_scenarios,
    asset_path,
    all_dm_methods_args,
    all_dm_methods_props_args,
)


def test_start():
    command = ["sleep", "1"]
    dapp = start_dapp(command)

    pid = dapp.pid
    assert pid is not None

    process = psutil.Process(dapp.pid)
    assert process.cmdline() == command


def test_list():
    dapp_1 = start_dapp(["echo", "foo"])
    sleep(
        0.01
    )  # ensure second dapp is created after the first (we test the app_id order)
    dapp_2 = start_dapp(["echo", "bar"])

    assert DappManager.list() == [dapp_1.app_id, dapp_2.app_id]


def test_prune():
    dapp_1 = start_dapp(["echo", "foo"])
    sleep(0.01)
    dapp_2 = start_dapp(["sleep", "1"])
    sleep(0.01)

    #   First dapp is already dead, but we don't know this yet
    assert DappManager.prune() == []
    assert DappManager.list() == [dapp_1.app_id, dapp_2.app_id]

    #   Check what is alive and what is not
    dapp_1.alive
    dapp_2.alive

    #   First one should get pruned now
    assert DappManager.prune() == [dapp_1.app_id]
    assert DappManager.list() == [dapp_2.app_id]

    #   And subsequent prunes should change nothing
    assert DappManager.prune() == []
    assert DappManager.list() == [dapp_2.app_id]


@pytest.mark.parametrize("get_dapp", get_dapp_scenarios)
def test_stop(get_dapp):
    dapp = get_dapp(["sleep", "3"])
    pid = dapp.pid
    assert process_is_running(pid)

    #   NOTE: `stop` is not guaranted to succeed for every process (because it only SIGINTs),
    #         but it for sure should succeed for the command we're running here
    assert dapp.alive
    assert dapp.stop(timeout=1)
    assert not dapp.alive
    sleep(0.01)
    assert not process_is_running(pid)


@pytest.mark.parametrize("get_dapp", get_dapp_scenarios)
def test_stop_timeout_kill(get_dapp):
    dapp = get_dapp([asset_path("sleep_no_sigint.sh"), "10"])
    pid = dapp.pid
    sleep(0.01)

    #   stop times out because command ignores sigint
    assert dapp.alive
    assert not dapp.stop(timeout=1)
    assert dapp.alive
    assert process_is_running(pid)

    #   but this can't be ignored
    dapp.kill()
    assert not dapp.alive
    sleep(0.01)
    assert not process_is_running(pid)


@pytest.mark.parametrize("get_dapp", get_dapp_scenarios)
def test_read_file(get_dapp):
    dapp = get_dapp(
        [asset_path("write_mock_files.sh")], state_file=True, data_file=True
    )
    sleep(0.01)

    for file_type in ("state", "data"):
        mock_fname = asset_path(f"mock_{file_type}_file.txt")
        with open(mock_fname) as f:
            assert dapp.read_file(file_type) == f.read()


@pytest.mark.parametrize(
    "method_name_args",
    all_dm_methods_props_args,
    ids=[x[0] for x in all_dm_methods_props_args],
)
def test_unknown_app(method_name_args):
    method_name, *args = method_name_args
    invalid_app_id = "oops_no_such_app"
    dapp = DappManager(invalid_app_id)
    with pytest.raises(UnknownApp) as exc_info:
        #   NOTE: we have both properties and methods here, exceptions for properties are
        #         raised in getattr, for methods when they are executed (*args), but both is fine
        #         so this doesn't really matter
        getattr(dapp, method_name)(*args)
    assert invalid_app_id in str(exc_info.value)


@pytest.mark.parametrize(
    "method_name_args",
    all_dm_methods_args,
    ids=[x[0] for x in all_dm_methods_args],
)
def test_app_not_running(method_name_args):
    method_name, *args = method_name_args
    dapp = start_dapp(["echo", "foo"])
    sleep(0.01)
    with pytest.raises(AppNotRunning) as exc_info:
        getattr(dapp, method_name)(*args)
    assert dapp.app_id in str(exc_info.value)


@pytest.mark.parametrize("file_type", ("state", "data"))
@pytest.mark.parametrize(
    "kwargs, raises",
    (
        ({"ensure_alive": True}, True),
        ({"ensure_alive": False}, False),
    ),
)
def test_app_not_running_ensure_alive(file_type, kwargs, raises):
    dapp = start_dapp(["echo", "foo"])
    sleep(0.01)
    if raises:
        with pytest.raises(AppNotRunning) as exc_info:
            dapp.read_file(file_type, **kwargs)
        assert dapp.app_id in str(exc_info.value)
    else:
        dapp.read_file(file_type, **kwargs)
