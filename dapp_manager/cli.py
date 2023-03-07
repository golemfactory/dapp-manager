import sys
from functools import wraps
from pathlib import Path
from typing import Optional, Tuple

import click
from dapp_runner.log import LOG_CHOICES

from dapp_manager import DappManager
from dapp_manager.autocomplete import install_autocomplete
from dapp_manager.exceptions import DappManagerException
from dapp_manager.storage import RunnerReadFileType


def _app_id_autocomplete(ctx, args, incomplete):  # noqa
    return [app_id for app_id in DappManager.list() if app_id.startswith(incomplete)]


def _with_app_id(wrapped_func):
    wrapped_func = click.argument("app-id", type=click.STRING, autocompletion=_app_id_autocomplete)(
        wrapped_func
    )
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
def cli():
    pass


@cli.command()
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
@click.option(
    "--log-level",
    type=click.Choice(LOG_CHOICES, case_sensitive=False),
)
@_capture_api_exceptions
def start(descriptors: Tuple[Path], *, config: Path, log_level: Optional[str]):
    """Start a new app using the provided descriptor and config files."""
    dapp = DappManager.start(*descriptors, config=config, log_level=log_level)
    print(dapp.app_id)


@cli.command()
@_capture_api_exceptions
def list():
    """List known app IDs (both active and dead).

    The results are sorted by the apps' creation time.
    """
    app_ids = DappManager.list()
    if app_ids:
        print("\n".join(app_ids))


@cli.command()
@_capture_api_exceptions
def prune():
    """Remove data for non-running apps.

    This removes all data related to those apps, including logs, state etc.
    """
    app_ids = DappManager.prune()
    if app_ids:
        print("\n".join(app_ids))


@cli.command()
@click.option(
    "--timeout",
    "-t",
    type=int,
    default=10,
    help="Specify a shutdown timeout in seconds. Successful shutdown is indicated by"
    " the app_id print",
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


@cli.command()
@_with_app_id
@_capture_api_exceptions
def kill(*, app_id):
    """Stop the given app forcibly.

    Stops the app's process using SIGKILL.
    """
    dapp = DappManager(app_id)
    dapp.kill()
    print(app_id)


@cli.command()
@_with_app_id
@click.argument("service", required=True, type=str)
@click.argument(
    "command",
    nargs=-1,
    required=True,
    type=str,
)
@click.option(
    "--timeout",
    type=int,
    default=60,
)
@_capture_api_exceptions
def exec(*, app_id, service, command, timeout):
    dapp = DappManager(app_id)
    dapp.exec_command(service, command, timeout)


@cli.command()
@_with_app_id
@click.argument("file-type", type=click.Choice(["state", "data", "log", "stdout", "stderr"]))
@click.option(
    "--ensure-alive/--no-ensure-alive",
    default=True,
)
@click.option(
    "-f",
    "--follow",
    is_flag=True,
    default=False,
)
@_capture_api_exceptions
def read(app_id: str, file_type: RunnerReadFileType, ensure_alive: bool, follow: bool):
    """Read output from the given app."""

    dapp = DappManager(app_id)

    if follow:
        for chunk in dapp.read_file_follow(file_type, ensure_alive=ensure_alive):
            print(chunk, end="")
    else:
        print(dapp.read_file(file_type, ensure_alive=ensure_alive))


@cli.command()
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

    This command works by appending a pre-defined piece of shell code to the user's shell
    configuration file.

    The default target file will depend on the selected shell type (bash, fish or zsh):
        - bash: `~/.bashrc`
        - fish: `~/.config/fish/completions/{script_name}.fish`
        - zsh: `~/.zshrc`
    Use the `--path` flag to override the default target file.

    The command does nothing if the target file already contains the completion code.
    """
    install_autocomplete(shell, path)
