import base64
import logging
from functools import wraps
import sys
import asyncio
import json
from pathlib import Path
from typing import Tuple, Dict

import aiohttp
import click
from aiohttp.hdrs import CONTENT_LENGTH
from dapp_runner.descriptor.parser import load_yamls
from yapapi.payload.vm import resolve_repo_srv, _DEFAULT_REPO_SRV

from dapp_runner.descriptor import DappDescriptor
from dapp_stats import DappStats

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
def size(descriptors: Tuple[Path]):
    """Calculates dApp defined payloads sizes (in bytes) on the provided set of descriptor files."""

    logger.debug('Loading dApp descriptors...')
    dapp_dict = load_yamls(*descriptors)
    dapp = DappDescriptor.load(dapp_dict)

    logger.debug('Loading dApp descriptors done')

    logger.debug(f'Measuring sizes of "{len(dapp.payloads)}" defined payloads...')
    payloads_sizes: Dict[str, int] = {}
    for payload_name, payload in dapp.payloads.items():

        async def get_image_size(image_url):
            async with aiohttp.ClientSession() as client:
                resp = await client.head(image_url)
                if resp.status != 200:
                    resp.raise_for_status()

                return int(resp.headers[CONTENT_LENGTH])

        if payload.runtime == 'vm':
            image_hash = payload.params.get('image_hash')
            if image_hash is None:
                message = f'Ignoring payload "{payload_name}" as "image_hash" is not present in params'
                logger.debug(message)
                click.echo(message, err=True)
                continue

            async def resolve_package_repo_url(repo_url, image_hash):
                async with aiohttp.ClientSession() as client:
                    resp = await client.get(f"{repo_url}/image.{image_hash}.link")
                    if resp.status != 200:
                        resp.raise_for_status()

                    return await resp.text()

            repo_url = resolve_repo_srv(_DEFAULT_REPO_SRV)
            loop = asyncio.get_event_loop()
            image_url = loop.run_until_complete(resolve_package_repo_url(repo_url, image_hash))

            payload_size = loop.run_until_complete(get_image_size(image_url))
            payloads_sizes[payload_name] = payload_size
        elif payload.runtime == 'vm/manifest':
            manifest_hash = payload.params.get('manifest')
            if manifest_hash is None:
                message = f'Ignoring payload "{payload_name}" as "manifest" is not present in params'
                logger.debug(message)
                click.echo(message, err=True)
                continue

            manifest = json.loads(base64.b64decode(manifest_hash.encode('utf-8')))

            image_url = manifest['payload'][0]['urls'][0]

            loop = asyncio.get_event_loop()
            payload_size = loop.run_until_complete(get_image_size(image_url))
            payloads_sizes[payload_name] = payload_size
        else:
            message = f'Ignoring payload "{payload_name}" as size measurement for runtime "{payload.runtime}" is not ' \
                      f'supported'
            logger.debug(message)
            click.echo(message, err=True)

    logger.debug('Measuring sizes of defined payloads done')

    click.echo(json.dumps({'total_size': sum(payloads_sizes.values()), 'payloads': payloads_sizes}))


def main():
    _cli()


if __name__ == "__main__":
    main()
