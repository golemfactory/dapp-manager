#!/usr/bin/env python3

# Script that has a similar interface to the dapp-runner,
# but only prints some things to the screen/files and waits forever.
# Useful for testing.

from pathlib import Path
from time import sleep
from typing import Tuple
from itertools import count
from random import random

import click


@click.group()
def _cli():
    pass


@_cli.command()
@click.option(
    "--data",
    "-d",
    required=True,
    type=Path,
    help="Path to the data file.",
)
@click.option(
    "--state",
    "-s",
    required=True,
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
):
    print("mock_dapp_runner start", descriptors, kwargs)

    data_file = open(kwargs["data"], "w", buffering=1)
    state_file = open(kwargs["state"], "w", buffering=1)

    try:
        for i in count(1):
            state_file.write(f"Running for {i} seconds\n")
            if i == 3:
                data_file.write(f"Important data received: {random()}\n")
            sleep(1)
    except KeyboardInterrupt:
        state_file.write("Shutting down\n")
        sleep(3)
        state_file.write("Graceful shutdown finished\n")
        data_file.close()
        state_file.close()


if __name__ == "__main__":
    _cli()
