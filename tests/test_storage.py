from pathlib import Path

import pytest

from dapp_manager.exceptions import UnknownApp
from dapp_manager.storage import SimpleStorage


def test_storage_data_dir():
    storage = SimpleStorage("foo", "/bar")
    assert storage._data_dir.resolve() == Path("/bar/foo").resolve()


def test_storage_app_id_special_chars():
    storage = SimpleStorage("..foo", "/bar")
    assert storage._data_dir.resolve() == Path("/bar/foo").resolve()


def test_storage_app_id_disallows_traversal():
    storage = SimpleStorage("", "/bar")
    storage.app_id = "../foo"
    with pytest.raises(UnknownApp):
        storage._data_dir.resolve()
