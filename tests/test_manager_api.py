'''A bunch of E2E tests of the DappManager interface'''
from unittest import mock
from pathlib import Path
import os
import psutil
import pytest
import uuid

from yagna_dapp_manager import DappManager
from yagna_dapp_manager.storage import SimpleStorage


@pytest.fixture
def test_dir(monkeypatch):
    """Replace the default data dir with a new one, remove directory later"""
    test_dir_name = '{}'.format(uuid.uuid4().hex)
    SimpleStorage._data_dir = Path(test_dir_name)

    yield

    try:
        os.rmdir(test_dir_name)
    except OSError:
        pass


def test_start(test_dir):
    """Start a mocked runner, ensure dapp.pid is correct"""

    command = ['sleep', '1']
    descriptor_file = '.gitignore'  # any existing file will do
    config_file = '.gitignore'  # any existing file will do

    with mock.patch("yagna_dapp_manager.dapp_starter.DappStarter._get_command") as _get_command:
        _get_command.return_value = command

        dapp = DappManager.start(descriptor_file, config=config_file)

    pid = dapp.pid
    assert pid is not None

    process = psutil.Process(dapp.pid)
    assert process.cmdline() == command
