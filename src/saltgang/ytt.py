import argparse
import logging
import pathlib
import re
import subprocess
from dataclasses import dataclass
from typing import List

from saltgang import logger as loggermod

_logger = logging.getLogger(__name__)


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


@dataclass(init=False)
class YttParams:
    main: pathlib.Path
    values: List[pathlib.Path]
    out: pathlib.Path

    def __init__(self, main: str, values: List[str], out: str) -> None:
        self.main = pathlib.Path(main)
        self.values = [pathlib.Path(x) for x in values]
        self.out = pathlib.Path(out)

    def validate(self):
        for path in [self.main, *self.values]:
            if not path.exists():
                raise FileNotFoundError(path)


class Ytt:
    def __init__(self):
        _logger.debug(f"creating instance of {type(self)}")
        self.installed = None
        self.check_installed()

    def check_installed(self):
        process = subprocess.Popen(
            "ytt version",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        try:
            stdout, stderr = process.communicate()
            if stderr:
                raise ValueError(stderr.decode())

            if not re.search(r"ytt version \d+\.\d+", stdout.decode()):
                raise ValueError("Can't find ytt installed")
            self.installed = True
        except ValueError as ex:
            self.logger.exception(ex)
            self.installed = False


def main(args):
    Ytt()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    add_arguments(parser)
    args = parser.parse_args()
    loggermod.setup_logging(args.loglevel)

    main(args)
