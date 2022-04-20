from pathlib import Path
from typing import Tuple

import click

from .dapp_manager import DappManager


def _with_app_id(wrapped_func):
    wrapped_func = click.option(
        "--app-id",
        type=str,
        required=True,
        help="ID of an existing distributed application.",
    )(wrapped_func)
    return wrapped_func


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
def start(descriptors: Tuple[Path], *, config: Path):
    dapp = DappManager.start(*descriptors, config=config)
    print(dapp.app_id)


@_cli.command()
def list():
    app_ids = DappManager.list()
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
def stop(*, app_id: str, timeout: int):
    dapp = DappManager(app_id)
    if dapp.stop(timeout):
        print(app_id)


@_cli.command()
@_with_app_id
def kill(*, app_id):
    dapp = DappManager(app_id)
    dapp.kill()
    print(app_id)


@_cli.command()
@_with_app_id
def raw_state(*, app_id):
    dapp = DappManager(app_id)
    print(dapp.raw_state())


@_cli.command()
@_with_app_id
def raw_data(*, app_id):
    dapp = DappManager(app_id)
    print(dapp.raw_data())


if __name__ == "__main__":
    _cli()
