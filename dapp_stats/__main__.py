import click
from exceptions import DappStatsException
from functools import wraps
import json
from pathlib import Path
import sys

from dapp_stats import DappStats


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


def main():
    _cli()


if __name__ == "__main__":
    main()
