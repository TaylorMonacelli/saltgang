import argparse
import logging
import sys

from saltgang import __version__, fetch, meta, panel, quickstart, settings


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


parser = subparsers.add_parser(
    "encassist",
    aliases=["enc"],
    help="using ytt, merge specific encassist variables into global encassist.yml",
)
parser.add_argument(
    "--config-basedir",
    help=(
        "Provide the base directry path to encassist.yml yaml"
        " files.  For example, if you did:"
        " 'git clone https://gitlab.com/streambox/spectra_encassist tmp' "
        " then you would provide this '--config-basedir tmp'."
    ),
)
parser.add_argument(
    "--conf",
    help="path to config.yml",
)
parser.add_argument(
    "--outpath",
    help="provide the path to where to write the resulting encassist yaml file",
)
parser.add_argument(
    "--sku",
    help="",
    choices=["macos", "linux", "avid", "universal"],
    required=True,
)


fetch.add_parser(subparsers)
meta.add_parser(subparsers)
panel.add_parser(subparsers)
quickstart.add_parser(subparsers)
settings.add_parser(subparsers)
