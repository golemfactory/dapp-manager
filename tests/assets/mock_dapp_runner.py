#!/usr/bin/env python3

# Script that has a similar interface to the dapp-runner,
# but only prints some things to the screen/files and waits forever.
# Useful for testing.

import sys
from itertools import count
from pathlib import Path
from random import random
from time import sleep
from typing import Dict, TextIO, Tuple

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
    "--stdout",
    type=Path,
    help="Redirect stdout to the specified file.",
)
@click.option(
    "--stderr",
    type=Path,
    help="Redirect stderr to the specified file.",
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

    streams: Dict[str, TextIO] = {
        k: sys.stdout for k in ["data", "state", "log", "stdout", "stderr"]
    }

    for kwarg in streams.keys():
        if kwargs.get(kwarg):
            streams[kwarg] = open(kwargs[kwarg], "w", buffering=1)

    try:
        streams["log"].write("engine started...")
        for i in count(1):
            streams["state"].write(f"Running for {i} seconds\n")

            if i == 3:
                data = str(random())
                streams["data"].write(data)
                streams["stdout"].write(f"Important data received: {data}\n")
            sleep(1)
    except KeyboardInterrupt:
        streams["state"].write("Shutting down\n")
        sleep(3)
        streams["log"].write("engine stopped.")
        streams["state"].write("Graceful shutdown finished\n")
        for stream in streams.values():
            stream.close()


if __name__ == "__main__":
    _cli()
