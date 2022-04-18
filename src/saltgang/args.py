import argparse
import logging
import sys

from saltgang import __version__, encassist, fetch, meta, panel, quickstart, settings


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

encassist.add_parser(subparsers)
fetch.add_parser(subparsers)
meta.add_parser(subparsers)
panel.add_parser(subparsers)
quickstart.add_parser(subparsers)
settings.add_parser(subparsers)
