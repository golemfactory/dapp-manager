from functools import wraps
from pathlib import Path
from typing import Tuple
import sys

import click

from yagna_dapp_manager import DappManager
from yagna_dapp_manager.autocomplete import install_autocomplete
from yagna_dapp_manager.exceptions import DappManagerException


def _with_app_id(wrapped_func):
    wrapped_func = click.argument(
        "app-id",
        type=str,
    )(wrapped_func)
    return wrapped_func


def _with_ensure_alive(wrapped_func):
    wrapped_func = click.option(
        "--ensure-alive/--no-ensure-alive",
        default=True,
    )(wrapped_func)
    return wrapped_func


def _capture_api_exceptions(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except DappManagerException as e:
            print(str(e), file=sys.stderr)
            sys.exit(e.SHELL_EXIT_CODE)

    return wrapped


@click.group()
def _cli():
    pass


@_cli.command()
@click.option(
    "--config",
    "-c",
    required=True,
    type=Path,
    help="Path to the file containing yagna-specific config.",
)
@click.argument(
    "descriptors",
    nargs=-1,
    required=True,
    type=Path,
)
@_capture_api_exceptions
def start(descriptors: Tuple[Path], *, config: Path):
    dapp = DappManager.start(*descriptors, config=config)
    print(dapp.app_id)


@_cli.command()
@_capture_api_exceptions
def list():
    app_ids = DappManager.list()
    if app_ids:
        print("\n".join(app_ids))


@_cli.command()
@_capture_api_exceptions
def prune():
    app_ids = DappManager.prune()
    if app_ids:
        print("\n".join(app_ids))


@_cli.command()
@click.option(
    "--timeout",
    "-t",
    type=int,
    default=10,
    help="Specify a shutdown timeout in seconds. Successful shutdown is indicated by the app_id print",
)
@_with_app_id
@_capture_api_exceptions
def stop(*, app_id: str, timeout: int):
    dapp = DappManager(app_id)
    if dapp.stop(timeout):
        print(app_id)


@_cli.command()
@_with_app_id
@_capture_api_exceptions
def kill(*, app_id):
    dapp = DappManager(app_id)
    dapp.kill()
    print(app_id)


@_cli.group()
def read():
    pass


@read.command()
@_with_app_id
@_capture_api_exceptions
@_with_ensure_alive
def state(*, app_id, ensure_alive):
    dapp = DappManager(app_id)
    print(dapp.read_file("state", ensure_alive))


@read.command()
@_with_app_id
@_capture_api_exceptions
@_with_ensure_alive
def data(*, app_id, ensure_alive):
    dapp = DappManager(app_id)
    print(dapp.read_file("data", ensure_alive))


@_cli.command()
@_with_app_id
@_capture_api_exceptions
@_with_ensure_alive
def log(*, app_id, ensure_alive):
    dapp = DappManager(app_id)
    print(dapp.read_file("log", ensure_alive))


@_cli.command()
@_with_app_id
@_capture_api_exceptions
@_with_ensure_alive
def stdout(*, app_id, ensure_alive):
    dapp = DappManager(app_id)
    print(dapp.read_file("stdout", ensure_alive))


@_cli.command()
@_with_app_id
@_capture_api_exceptions
@_with_ensure_alive
def stderr(*, app_id, ensure_alive):
    dapp = DappManager(app_id)
    print(dapp.read_file("stderr", ensure_alive))


@_cli.command()
@click.argument("shell", type=click.Choice(["bash", "fish", "zsh"]))
@click.option("--path", "-p", type=Path, default=None)
def autocomplete(shell: str, path: Path):
    """Enable shell completion by registering an appropriate shell function.
    
    This command works by appending a predefined piece of shell code to the user's 
    shell configuration file.
    The target file will depend on the selected shell type (bash, fish or zsh).
    The command does nothing if the target file already contains the completion code.
    """
    install_autocomplete(shell, path)


def main():
    _cli()


if __name__ == "__main__":
    main()
