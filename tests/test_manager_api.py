"""A bunch of E2E tests of the DappManager interface"""
import psutil
import pytest
from time import sleep

from yagna_dapp_manager import DappManager

from .helpers import start_dapp, process_is_running, get_dapp_scenarios, asset_path


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


@pytest.mark.parametrize("get_dapp", get_dapp_scenarios)
def test_stop(get_dapp):
    dapp = get_dapp(["sleep", "3"])
    assert process_is_running(dapp.pid)

    #   NOTE: `stop` is not guaranted to succeed for every process (because it only SIGINTs),
    #         but it for sure should succeed for the command we're running here
    assert dapp.stop(timeout=1)
    sleep(0.01)
    assert not process_is_running(dapp.pid)


@pytest.mark.parametrize("get_dapp", get_dapp_scenarios)
def test_stop_timeout_kill(get_dapp):
    dapp = get_dapp([asset_path("sleep_no_sigint.sh"), "10"])
    sleep(0.01)

    #   stop times out because command ignores sigint
    assert not dapp.stop(timeout=1)
    assert process_is_running(dapp.pid)

    #   but this can't be ignored
    dapp.kill()
    sleep(0.01)
    assert not process_is_running(dapp.pid)


@pytest.mark.parametrize("get_dapp", get_dapp_scenarios)
def test_raw_status_raw_data(get_dapp):
    dapp = get_dapp(
        [asset_path("write_mock_files.sh")], status_file=True, data_file=True
    )
    sleep(0.01)

    with open(asset_path("mock_status_file.txt")) as f:
        assert dapp.raw_status() == f.read()

    with open(asset_path("mock_data_file.txt")) as f:
        assert dapp.raw_data() == f.read()
