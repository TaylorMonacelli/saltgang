import argparse
import configparser
import logging
import pathlib
import platform
import subprocess
import sys
import tempfile

from saltgang import common
from saltgang import logger as loggermod


def add_arguments(parser):
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


def add_parser(subparsers):
    parser = subparsers.add_parser("url", help="show the url of where we push zip")
    add_arguments(parser)


def to_clipboard(text):
    if platform.system() not in ["Darwin"]:
        print("pbcopy is not suported", file=sys.stderr)
        return

    tmpfilepath = pathlib.Path(tempfile.gettempdir()) / "spectra.txt"
    tmpfilepath.unlink(missing_ok=True)
    tmpfilepath.write_text(text)

    pbcopy = subprocess.Popen(
        f"pbcopy <{str(tmpfilepath)}",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
    )
    stdout, stderr = pbcopy.communicate()
    if stderr:
        print("couldn't copy to clipboard", file=sys.stderr)


def main(args):
    cwd = pathlib.Path.cwd()

    if "spectra_installer" not in cwd.parts:
        print("make sure you're in spectra_installer project folder", file=sys.stderr)
        sys.exit(-1)

    ini = configparser.RawConfigParser()
    config = common.project_path() / ".bumpversion.cfg"
    ini.read(config)
    dct = dict(ini.items("bumpversion"))
    version = dct["current_version"]

    urls = f"""
https://streambox-spectra.s3-us-west-2.amazonaws.com/{version}/spectra_win_{version}.zip
https://streambox-spectra.s3-us-west-2.amazonaws.com/{version}/win/spectra.zip
https://streambox-spectra.s3-us-west-2.amazonaws.com/{version}/win/avid/spectra.exe
https://streambox-spectra.s3-us-west-2.amazonaws.com/{version}/win/universal/spectra.exe
    """.strip()

    urls = f"""
https://streambox-spectra.s3-us-west-2.amazonaws.com/{version}/win/spectra_win_{version}.zip
    """.strip()

    to_clipboard(urls)
    print(urls)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    add_arguments(parser)
    args = parser.parse_args()
    loggermod.setup_logging(args.loglevel)

    main(args)
