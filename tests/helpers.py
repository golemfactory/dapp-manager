from unittest import mock
import psutil
from typing import List, Tuple, Union

from yagna_dapp_manager import DappManager


def process_is_running(pid: int) -> bool:
    try:
        process = psutil.Process(pid)

        #   TODO: https://github.com/golemfactory/dapp-manager/issues/9
        return process.status() != psutil.STATUS_ZOMBIE
    except psutil.NoSuchProcess:
        return False


def start_dapp(
    base_command: List[str], state_file=False, data_file=False
) -> DappManager:
    """Executes DappManager.start(), but executed command is replaced by base_command

    If state_file is True, state file name will be added as command line arg.
    Same for data_file, if both are True state_file goes first."""

    descriptor_file = ".gitignore"  # any existing file will do (for now)
    config_file = ".gitignore"  # any existing file will do (for now)

    def _get_command(self):
        command = base_command.copy()
        if state_file:
            command = command + [str(self.storage.file_name("state").resolve())]
        if data_file:
            command = command + [str(self.storage.file_name("data").resolve())]
        return command

    with mock.patch(
        "yagna_dapp_manager.dapp_starter.DappStarter._get_command", new=_get_command
    ):
        return DappManager.start(descriptor_file, config=config_file)


def new_dapp_manager(command, **kwargs) -> DappManager:
    """Start a dapp, return a new DappManager instance"""
    dapp = start_dapp(command, **kwargs)
    return DappManager(dapp.app_id)


def other_dapp_in_between(command, **kwargs) -> DappManager:
    """Start a dapp, start another dapp, return DappManager for the first one"""
    dapp = start_dapp(command, **kwargs)
    start_dapp(["echo", "foo"])
    return DappManager(dapp.app_id)


# Collection of functions with the same interface as start_dapp,
# with different internal "scenarios". Tests performed on a running dapp should
# be run in every scenario.
# Purpose:
#   *   ensure DappManager is stateless
#   *   ensure multiple dapps don't interfere with each other
get_dapp_scenarios = (
    start_dapp,
    new_dapp_manager,
    other_dapp_in_between,
    #   TODO (?): Start dapp in another process, do something from this process
    #   TODO (?): CLI scenarios, when we have CLI
)


def asset_path(name):
    return f"tests/assets/{name}"


#   All instance methods/propeties, with sample args
#   (Possible TODO: it would be probably better to create this in a dynamic way,
#   using inspect - now we risk that some new method will not be tested).
#   ALSO: probably the best solution is to just remove this and have explicit listings
all_dm_methods_args: Tuple[Union[Tuple[str], Tuple[str, int], Tuple[str, str]], ...] = (
    ("read_file", "state"),
    ("read_file", "data"),
    ("stop", 1),
    ("kill",),
)
all_dm_methods_props_args = all_dm_methods_args + (("alive",), ("pid",))
