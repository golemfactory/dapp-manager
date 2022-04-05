'''A bunch of E2E tests of the DappManager interface'''
from unittest import mock
from pathlib import Path
import os
import psutil
import pytest
import uuid
from time import sleep

from yagna_dapp_manager import DappManager
from yagna_dapp_manager.storage import SimpleStorage


@pytest.fixture
def test_dir(monkeypatch):
    """Replace the default data dir with a new one, remove directory later"""
    test_dir_name = '/tmp/{}'.format(uuid.uuid4().hex)
    SimpleStorage.DEFAULT_BASE_DIR = Path(test_dir_name)

    yield

    try:
        os.rmdir(test_dir_name)
    except OSError:
        pass


def start_dapp(base_command, status_file=False, data_file=False):
    descriptor_file = '.gitignore'  # any existing file will do
    config_file = '.gitignore'  # any existing file will do

    def _get_command(self):
        command = base_command.copy()
        if status_file:
            command = command + [str(self.storage.status_file.resolve())]
        if data_file:
            command = command + [str(self.storage.data_file.resolve())]
        return command

    with mock.patch("yagna_dapp_manager.dapp_starter.DappStarter._get_command", new=_get_command):
        return DappManager.start(descriptor_file, config=config_file)


def process_is_running(pid):
    try:
        process = psutil.Process(pid)

        #   TODO
        #   Is there any way **not** to have defunct processes, but just make them
        #   disappear forever? Or maybe this isn't harmful at all? We'd rather
        #   avoid having thousands of defunct processes when using a single
        #   process to manage multiple apps.
        return process.status() != psutil.STATUS_ZOMBIE
    except psutil.NoSuchProcess:
        return False


def test_start(test_dir):
    command = ['sleep', '1']
    dapp = start_dapp(command)

    pid = dapp.pid
    assert pid is not None

    process = psutil.Process(dapp.pid)
    assert process.cmdline() == command


def test_list(test_dir):
    dapp_1 = start_dapp(['echo', 'foo'])
    sleep(0.01)  # ensure second dapp is created after the first (we test the app_id order)
    dapp_2 = start_dapp(['echo', 'bar'])

    assert DappManager.list() == [dapp_1.app_id, dapp_2.app_id]


@pytest.mark.parametrize('create_dapp_manager', (
    #   Start and stop with the same manager instance
    start_dapp,

    #   Stop with another manager instance then the one that started
    lambda command: DappManager(start_dapp(command).app_id),

    #   TODO
    #   Start in a process, get app_id, stop in this process
))
def test_stop(test_dir, create_dapp_manager):
    dapp = create_dapp_manager(['sleep', '3'])
    assert process_is_running(dapp.pid)

    #   NOTE: `stop` is not guaranted to succeed for every process (because it only SIGINTs),
    #         but it for sure should succeed for the command we're running here
    assert dapp.stop(1)
    sleep(0.01)  # wait just a moment for the process to stop
    assert not process_is_running(dapp.pid)


def test_stop_timeout_kill(test_dir):
    dapp = start_dapp(['tests/sleep_no_sigint.sh', '10'])
    sleep(0.01)

    #   stop times out because command ignores sigint
    assert not dapp.stop(1)
    assert process_is_running(dapp.pid)

    #   but this can't be ignored
    dapp.kill()
    sleep(0.01)  # wait just a moment for the process to stop
    assert not process_is_running(dapp.pid)


def test_raw_status_raw_data(test_dir):
    dapp = start_dapp(['tests/write_mock_files.sh'], status_file=True, data_file=True)
    sleep(0.01)

    with open('tests/mock_status_file.txt') as f:
        assert dapp.raw_status() == f.read()

    with open('tests/mock_data_file.txt') as f:
        assert dapp.raw_data() == f.read()
