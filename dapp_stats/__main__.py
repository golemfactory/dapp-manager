import base64
import logging
from functools import wraps
import sys
import asyncio
import json
from pathlib import Path
from typing import Tuple, Dict, Sequence

import aiohttp
import click
from aiohttp.hdrs import CONTENT_LENGTH
from dapp_runner.descriptor.parser import load_yamls
from yapapi.payload.vm import resolve_repo_srv, _DEFAULT_REPO_SRV

from dapp_runner.descriptor import DappDescriptor
from dapp_stats import DappStats
from dapp_stats.dapp_size_resolver import DappSizeResolver

from .exceptions import DappStatsException


logger = logging.getLogger(__name__)

def _with_app_id(wrapped_func):
    wrapped_func = click.argument("app-id", type=str)(wrapped_func)
    return wrapped_func


def _capture_api_exceptions(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except DappStatsException as e:
            print(str(e), file=sys.stderr)
            sys.exit(e.SHELL_EXIT_CODE)

    return wrapped


@click.group()
def _cli():
    pass


@_cli.command()
@_with_app_id
@_capture_api_exceptions
def stats(*, app_id):
    """Returns the stats of a given app."""
    dapp = DappStats(app_id)
    print(json.dumps(dapp.get_stats(), indent=2, default=str))


@_cli.command()
@click.argument(
    "descriptors",
    nargs=-1,
    required=True,
    type=Path,
)
def size(descriptors: Sequence[Path]):
    """Calculates dApp defined payloads sizes (in bytes) on the provided set of descriptor files."""

    measured_sizes, errors = DappSizeResolver.resolve_payload_size(descriptors)

    for error in errors:
        click.echo(error, err=True)

    click.echo(json.dumps(measured_sizes))


def main():
    _cli()


if __name__ == "__main__":
    main()
