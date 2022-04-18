import argparse
import logging
import sys

from saltgang import __version__


def _error(parser):
    def wrapper(interceptor):
        parser.print_help()
        sys.exit(-1)

    return wrapper


def add_common_args(parser):
    parser.add_argument(
        "-v",
        "--verbose",
        dest="loglevel",
        help="set loglevel to INFO",
        action="store_const",
        const=logging.INFO,
    )
    parser.add_argument(
        "-vv",
        "--very-verbose",
        dest="loglevel",
        help="set loglevel to DEBUG",
        action="store_const",
        const=logging.DEBUG,
    )


parser = argparse.ArgumentParser()
add_common_args(parser)
parser.add_argument(
    "--version",
    action="version",
    version="saltgang {ver}".format(ver=__version__),
)


parser.error = _error(parser)

subparsers = parser.add_subparsers(
    description="valid subcommands",
    title="subcommands",
    help="sub command help",
    required=True,
    dest="command",
)
