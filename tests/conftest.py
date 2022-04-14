import pytest
import tempfile

from yagna_dapp_manager import DappManager


@pytest.fixture(autouse=True)
def simple_storage_test_dir(monkeypatch):
    """Replace the SimpleStorage default data directory with a temporary directory."""

    with tempfile.TemporaryDirectory(prefix="dapp-manager-tests-") as test_dir_name:
        monkeypatch.setattr(DappManager, "_get_data_dir", lambda: test_dir_name)
        yield