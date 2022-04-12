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
def start(descriptors: Tuple[Path], *, config):
    dapp = DappManager.start(*descriptors, config=config)
    print(dapp.app_id)


@_cli.command()
def list():
    app_ids = DappManager.list()
    print("\n".join(app_ids))


if __name__ == '__main__':
    _cli()
