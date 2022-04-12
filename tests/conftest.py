from pathlib import Path
import pytest
import tempfile

from yagna_dapp_manager.storage import SimpleStorage


@pytest.fixture(autouse=True)
def simple_storage_test_dir(monkeypatch):
    """Replace the SimpleStorage default data directory with a temporary directory."""

    with tempfile.TemporaryDirectory(prefix='dapp-manager-tests-') as test_dir_name:
        monkeypatch.setattr(SimpleStorage, "DEFAULT_BASE_DIR", Path(test_dir_name))
        yield
