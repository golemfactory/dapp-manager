import random
import string
import sys
from datetime import datetime, timedelta, timezone
from time import sleep
from typing import Iterator, Literal
from unittest import mock

import psutil
import pytest

from dapp_manager import DappManager
from dapp_manager.exceptions import AppNotRunning, StartupFailed, UnknownApp

from .helpers import (
    all_dm_methods_args,
    all_dm_methods_props_args,
    asset_path,
    get_dapp_scenarios,
    process_is_running,
    start_dapp,
)


def test_start():
    command = [sys.executable, asset_path("sleep.py"), "1"]
    dapp = start_dapp(command)

    pid = dapp.pid
    assert pid is not None

    process = psutil.Process(dapp.pid)
    assert process.cmdline() == command


def test_list():
    dapp_1 = start_dapp([sys.executable, asset_path("echo.py"), "foo"])
    sleep(0.01)  # ensure second dapp is created after the first (we test the app_id order)
    dapp_2 = start_dapp([sys.executable, asset_path("echo.py"), "bar"])

    assert DappManager.list() == [dapp_1.app_id, dapp_2.app_id]


def test_prune():
    dapp_1 = start_dapp([sys.executable, asset_path("echo.py"), "foo"])
    sleep(0.5)
    dapp_2 = start_dapp([sys.executable, asset_path("sleep.py"), "3"])
    sleep(0.5)

    #   First dapp is already dead, but we don't know this yet
    assert DappManager.prune() == []
    assert DappManager.list() == [dapp_1.app_id, dapp_2.app_id]

    #   Check what is alive and what is not
    assert not dapp_1.alive
    assert dapp_2.alive

    #   First one should get pruned now
    assert DappManager.prune() == [dapp_1.app_id]
    assert DappManager.list() == [dapp_2.app_id]

    #   And subsequent prunes should change nothing
    assert DappManager.prune() == []
    assert DappManager.list() == [dapp_2.app_id]


@pytest.mark.parametrize("get_dapp", get_dapp_scenarios)
def test_stop(get_dapp):
    dapp = get_dapp([sys.executable, asset_path("sleep.py"), "3"])
    pid = dapp.pid
    sleep(0.5)
    assert process_is_running(pid)

    # NOTE: `stop` is not guaranted to succeed for every process (because it only
    # SIGINTs), but it for sure should succeed for the command we're running here
    assert dapp.alive
    assert dapp.stop(timeout=1)
    assert not dapp.alive
    sleep(0.01)
    assert not process_is_running(pid)


@pytest.mark.parametrize("get_dapp", get_dapp_scenarios)
def test_stop_timeout_kill(get_dapp):
    dapp = get_dapp([sys.executable, asset_path("worker_no_sigint.py"), "10"])
    pid = dapp.pid
    sleep(0.5)  # give some time for process to set up no sigint

    #   stop times out because command ignores sigint
    assert dapp.alive
    assert not dapp.stop(timeout=1)
    assert dapp.alive
    assert process_is_running(pid)

    #   but this can't be ignored
    dapp.kill()
    assert not dapp.alive
    sleep(0.5)
    assert not process_is_running(pid)


@pytest.mark.parametrize("get_dapp", get_dapp_scenarios)
@pytest.mark.parametrize("file_type", ("state", "data"))
def test_read_file(get_dapp, file_type):
    dapp = get_dapp(
        [sys.executable, asset_path("worker_with_log_files.py")], state_file=True, data_file=True
    )
    sleep(0.5)

    mock_fname = asset_path(f"mock_{file_type}_file.txt")
    with open(mock_fname) as f:
        assert dapp.read_file(file_type) == f.read()


@pytest.mark.parametrize("get_dapp", get_dapp_scenarios)
@pytest.mark.parametrize("file_type", ("state", "data"))
def test_read_file_follow(get_dapp, file_type):
    dapp = get_dapp(
        [sys.executable, asset_path("worker_with_log_files.py")], state_file=True, data_file=True
    )
    assert dapp.alive

    sleep(0.5)  # Wait for logs to be created

    additional_line = f"some\nmore\n{file_type}\nlines!"
    mock_fname = asset_path(f"mock_{file_type}_file.txt")

    iterator = dapp.read_file_follow(file_type)

    try:
        with open(mock_fname) as f:
            assert next(iterator) == f.read()

        with dapp.storage.file_name(file_type).open("a") as file:
            file.write(additional_line)

        assert next(iterator) == additional_line

    finally:
        iterator.close()


@pytest.mark.parametrize("get_dapp", get_dapp_scenarios)
@pytest.mark.parametrize("file_type", ("state", "data"))
def test_read_file_follow_not_running_initially(get_dapp, file_type):
    dapp = get_dapp(
        [sys.executable, asset_path("worker_with_log_files.py")], state_file=True, data_file=True
    )
    assert dapp.alive

    dapp.kill()

    assert not dapp.alive

    with pytest.raises(AppNotRunning):
        "".join(dapp.read_file_follow(file_type))


@pytest.mark.parametrize("get_dapp", get_dapp_scenarios)
@pytest.mark.parametrize("file_type", ("state", "data"))
def test_read_file_follow_logs_not_accessible_initially(get_dapp, file_type):
    dapp = get_dapp([sys.executable, asset_path("worker.py")], state_file=True, data_file=True)

    assert dapp.alive

    with pytest.raises(FileNotFoundError):
        next(dapp.read_file_follow(file_type))


@pytest.mark.parametrize("get_dapp", get_dapp_scenarios)
@pytest.mark.parametrize("file_type", ("state", "data"))
def test_read_file_follow_logs_not_accessible_after_some_time(get_dapp, file_type):
    dapp = get_dapp(
        [sys.executable, asset_path("worker_with_log_files.py")], state_file=True, data_file=True
    )
    assert dapp.alive

    sleep(0.5)  # Wait for logs to be created

    mock_fname = asset_path(f"mock_{file_type}_file.txt")

    iterator = dapp.read_file_follow(file_type)

    try:
        with open(mock_fname) as f:
            # read to end of file
            assert next(iterator) == f.read()

        # file should be closed, so we can externally remove log file
        dapp.storage.file_name(file_type).unlink()

        with pytest.raises(StopIteration):
            # as log file does not exist, StopIteraton should be raised
            next(iterator)

    finally:
        iterator.close()


@pytest.mark.parametrize("get_dapp", get_dapp_scenarios)
@pytest.mark.parametrize("file_type", ("state", "data"))
def test_read_file_follow_not_running_after_some_time(get_dapp, file_type):
    dapp = get_dapp(
        [sys.executable, asset_path("worker_with_log_files.py")], state_file=True, data_file=True
    )
    assert dapp.alive

    sleep(0.5)  # Wait for logs to be created

    mock_fname = asset_path(f"mock_{file_type}_file.txt")

    iterator = dapp.read_file_follow(file_type)

    try:
        with open(mock_fname) as f:
            # read to end of file
            assert next(iterator) == f.read()

        dapp.kill()

        with pytest.raises(StopIteration):
            # as app is not running, StopIteraton should be raised
            next(iterator)

    finally:
        iterator.close()


@pytest.mark.parametrize("get_dapp", get_dapp_scenarios)
def test_read_file_follow_chunk_size(get_dapp, mocker):
    mocker.patch("dapp_manager.dapp_manager.READ_FILE_CHUNK_SIZE", 5)

    dapp = get_dapp(
        [sys.executable, asset_path("worker_with_log_files.py")], state_file=True, data_file=True
    )

    assert dapp.alive

    sleep(0.5)  # Give some time to have log files prepared

    file_type = "state"
    additional_line = f"some\nmore\n{file_type}\nlines!"

    iterator = dapp.read_file_follow(file_type)

    try:
        # Content for following asserts are taken from "some\nmore\n{file_type}\nlines!" file
        assert next(iterator) == "THIS "
        assert next(iterator) == "IS\nA\n"
        assert next(iterator) == "STATE"
        assert next(iterator) == " FILE"
        assert next(iterator) == "!\n"

        with dapp.storage.file_name(file_type).open("a") as file:
            file.write(additional_line)

        # But for following asserts are taken from additional_line variable
        assert next(iterator) == "some\n"
        assert next(iterator) == "more\n"
        assert next(iterator) == file_type
        assert next(iterator) == "\nline"
        assert next(iterator) == "s!"

    finally:
        iterator.close()


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
        # NOTE: we have both properties and methods here, exceptions for properties are
        #  raised in getattr, for methods when they are executed (*args), but both are
        #  fine so this doesn't really matter
        data = getattr(dapp, method_name)(*args)

        if isinstance(data, Iterator):
            "".join(data)

    assert invalid_app_id in str(exc_info.value)


@pytest.mark.parametrize(
    "method_name_args",
    all_dm_methods_args,
    ids=[x[0] for x in all_dm_methods_args],
)
def test_app_not_running(method_name_args):
    method_name, *args = method_name_args
    dapp = start_dapp([sys.executable, asset_path("echo.py"), "foo"])
    sleep(0.5)
    with pytest.raises(AppNotRunning) as exc_info:
        data = getattr(dapp, method_name)(*args)

        if isinstance(data, Iterator):
            "".join(data)
    assert dapp.app_id in str(exc_info.value)


@pytest.mark.parametrize("file_type", ("state", "data"))
@pytest.mark.parametrize(
    "ensure_alive, exception_class",
    (
        (True, AppNotRunning),
        (False, FileNotFoundError),
    ),
)
def test_ensure_alive(file_type: Literal["state", "data"], ensure_alive, exception_class):
    dapp = start_dapp([sys.executable, asset_path("echo.py"), "foo"])
    sleep(1)

    with pytest.raises(exception_class) as exc_info:
        dapp.read_file(file_type, ensure_alive=ensure_alive)

    assert dapp.app_id in str(exc_info.value)


def test_startup_failed():
    old_dapp_list = DappManager.list()

    with pytest.raises(StartupFailed):
        start_dapp([sys.executable, asset_path("echo.py"), "foo"], check_startup_timeout=1)

    #   Ensure we don't preserve any data for the non-started dapp
    assert old_dapp_list == DappManager.list()


def test_not_my_app():
    dapp = start_dapp([sys.executable, asset_path("sleep.py"), "1"])
    sleep(0.01)

    assert dapp.alive

    with mock.patch(
        "dapp_manager.dapp_manager.psutil.Process.username",
        lambda _: "".join([random.choice(string.ascii_letters) for _ in range(8)]),
    ):
        assert not dapp.alive


def test_process_apparently_restarted():
    dapp = start_dapp([sys.executable, asset_path("sleep.py"), "1"])
    sleep(0.5)

    assert dapp.alive

    with mock.patch(
        "dapp_manager.dapp_manager.psutil.Process.create_time",
        lambda _: (datetime.now(tz=timezone.utc) + timedelta(minutes=5)).timestamp(),
    ):
        assert not dapp.alive
