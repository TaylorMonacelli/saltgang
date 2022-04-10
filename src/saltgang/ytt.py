import argparse
import logging
import pathlib
import re
import shlex
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
    outpath: pathlib.Path
    basedir: pathlib.Path = None

    def set_basedir(self, path: pathlib.Path) -> None:
        self.basedir = path

    def __init__(self, main: str, values: List[str], outpath: str) -> None:
        self.main = pathlib.Path(main)
        self.values = [pathlib.Path(x) for x in values]
        self.outpath = pathlib.Path(outpath)

    def validate(self):
        for path in [self.main, *self.values]:
            if not path.exists():
                raise FileNotFoundError(path)


class Ytt:
    def __init__(self, params):
        self.installed = None
        self.params = params
        self.check_installed()

    @classmethod
    def check_installed(cls):
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
            return True
        except ValueError as ex:
            _logger.exception(ex)

    def run(self):
        cmd = [
            "ytt",
            "--output",
            "yaml",
        ]

        x = ["--file", str(self.params.main.resolve())]
        cmd.extend(x)

        for param in self.params.values:
            x = []
            x.append("--file")
            x.append(str(param.resolve()))
            cmd.extend(x)

        cmdstr = shlex.join(cmd)
        _logger.debug(cmdstr)

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        stdout, stderr = process.communicate()
        if stderr:
            _logger.warning("{}".format(stderr.decode()))
        else:
            self.params.outpath.write_text(stdout.decode())


def main(args):
    Ytt()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    add_arguments(parser)
    args = parser.parse_args()
    loggermod.setup_logging(args.loglevel)

    main(args)
