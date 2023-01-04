import aiohttp
from aiohttp.hdrs import CONTENT_LENGTH
import asyncio
import base64
import click
from dapp_runner.descriptor import DappDescriptor
from dapp_runner.descriptor.parser import load_yamls
from functools import wraps
import json
import logging
from pathlib import Path
import sys
from typing import Dict, Sequence, Tuple
from yapapi.payload.vm import _DEFAULT_REPO_SRV, resolve_repo_srv

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

    measured_sizes, errors = DappSizeResolver.resolve_defined_payload_sizes(descriptors)

    for error in errors:
        click.echo(error, err=True)

    click.echo(json.dumps(measured_sizes, indent=2, default=str))


def main():
    _cli()


if __name__ == "__main__":
    main()
