#!/usr/bin/env python3

# Script that has a similar interface to the dapp-runner,
# but only prints some things to the screen/files and waits forever.
# Useful for testing.

from pathlib import Path
from time import sleep
from typing import Tuple, TextIO
from itertools import count
from random import random
import sys

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
    "--log",
    "-l",
    required=False,
    type=Path,
    help="Path to the log file.",
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

    log_file: TextIO
    if kwargs.get("log"):
        log_file = open(kwargs["log"], "w", buffering=1)
    else:
        log_file = sys.stdout

    try:
        log_file.write("engine started...")
        for i in count(1):
            state_file.write(f"Running for {i} seconds\n")

            if i == 3:
                data_file.write(f"Important data received: {random()}\n")
            sleep(1)
    except KeyboardInterrupt:
        state_file.write("Shutting down\n")
        sleep(3)
        log_file.write("engine stopped.")
        state_file.write("Graceful shutdown finished\n")
        data_file.close()
        state_file.close()
        log_file.close()


if __name__ == "__main__":
    _cli()
