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


def start_dapp(command):
    descriptor_file = '.gitignore'  # any existing file will do
    config_file = '.gitignore'  # any existing file will do

    with mock.patch("yagna_dapp_manager.dapp_starter.DappStarter._get_command") as _get_command:
        _get_command.return_value = command

        return DappManager.start(descriptor_file, config=config_file)


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
