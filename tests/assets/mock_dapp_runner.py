#!/usr/bin/env python3

# Script that has a similar interface to the dapp-runner,
# but only prints some things to the screen/files and waits forever.
# Useful for testing.

from pathlib import Path
from time import sleep
from typing import Tuple

import click


@click.group()
def _cli():
    pass


@_cli.command()
@click.option(
    "--data",
    "-d",
    type=Path,
    help="Path to the data file.",
)
@click.option(
    "--log",
    "-l",
    type=Path,
    help="Path to the log file.",
)
@click.option(
    "--state",
    "-s",
    type=Path,
    help="Path to the state file.",
)
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
def start(
    descriptors: Tuple[Path],
    **kwargs,
) -> str:
    print("mock_dapp_runner start", descriptors, kwargs)

    try:
        while True:
            print("still running!")
            sleep(1)
    except KeyboardInterrupt:
        print("Shutting down!")
        sleep(1)
        print("BYE")


if __name__ == '__main__':
    _cli()
