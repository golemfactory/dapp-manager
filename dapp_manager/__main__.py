from functools import wraps
from pathlib import Path
from typing import Tuple
import sys

import click

from dapp_manager import DappManager
from dapp_manager.autocomplete import install_autocomplete
from dapp_manager.exceptions import DappManagerException


def _app_id_autocomplete(_ctx, _param, incomplete):
    return [app_id for app_id in DappManager.list() if app_id.startswith(incomplete)]


def _with_app_id(wrapped_func):
    wrapped_func = click.argument(
        "app-id", type=str, shell_complete=_app_id_autocomplete
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
    """Start a new app using the provided descriptor and config files."""
    dapp = DappManager.start(*descriptors, config=config)
    print(dapp.app_id)


@_cli.command()
@_capture_api_exceptions
def list():
    """List known app IDs (both active and dead).

    The results are sorted by the apps' creation time.
    """
    app_ids = DappManager.list()
    if app_ids:
        print("\n".join(app_ids))


@_cli.command()
@_capture_api_exceptions
def prune():
    """Remove data for non-running apps.

    This removes all data related to those apps, including logs, state etc.
    """
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
    """Stop the given app gracefully.

    Requests a stop from the given app through a SIGINT.
    Optionally, a timeout (in seconds) may be given with --timeout flag.
    """
    dapp = DappManager(app_id)
    if dapp.stop(timeout):
        print(app_id)


@_cli.command()
@_with_app_id
@_capture_api_exceptions
def kill(*, app_id):
    """Stop the given app forcibly.

    Stops the app's process using SIGKILL.
    """
    dapp = DappManager(app_id)
    dapp.kill()
    print(app_id)


@_cli.group()
def read():
    """Read output from the given app."""
    # this function serves only to add a CLI command group
    # and so it doesn't need any body code
    pass


@read.command()
@_with_app_id
@_capture_api_exceptions
@_with_ensure_alive
def state(*, app_id, ensure_alive):
    """Read the state stream of the given app."""
    dapp = DappManager(app_id)
    print(dapp.read_file("state", ensure_alive))


@read.command()
@_with_app_id
@_capture_api_exceptions
@_with_ensure_alive
def data(*, app_id, ensure_alive):
    """Read the data stream of the given app."""
    dapp = DappManager(app_id)
    print(dapp.read_file("data", ensure_alive))


@read.command()
@_with_app_id
@_capture_api_exceptions
@_with_ensure_alive
def log(*, app_id, ensure_alive):
    """Read the log stream of a given app."""
    dapp = DappManager(app_id)
    print(dapp.read_file("log", ensure_alive))


@read.command()
@_with_app_id
@_capture_api_exceptions
@_with_ensure_alive
def stdout(*, app_id, ensure_alive):
    """Read the stdout of a given app."""
    dapp = DappManager(app_id)
    print(dapp.read_file("stdout", ensure_alive))


@read.command()
@_with_app_id
@_capture_api_exceptions
@_with_ensure_alive
def stderr(*, app_id, ensure_alive):
    """Read the stderr of a given app."""
    dapp = DappManager(app_id)
    print(dapp.read_file("stderr", ensure_alive))


@_cli.command()
@click.argument("shell", type=click.Choice(["bash", "fish", "zsh"]))
@click.option(
    "--path",
    "-p",
    type=Path,
    default=None,
    help="Path to the file to which the shell completion function should be added.",
)
def autocomplete(shell: str, path: Path):
    """Enable CLI shell completion for the given shell.

    This command works by appending a pre-defined piece of shell code to the user's
    shell configuration file.

    The default target file will depend on the selected shell type (bash, fish or zsh):
        - bash: `~/.bashrc`
        - fish: `~/.config/fish/completions/{script_name}.fish`
        - zsh: `~/.zshrc`
    Use the `--path` flag to override the default target file.

    The command does nothing if the target file already contains the completion code.
    """
    install_autocomplete(shell, path)


def main():
    _cli()


if __name__ == "__main__":
    main()
