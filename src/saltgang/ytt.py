import argparse
import logging
import pathlib
import re
import shlex
import subprocess
from dataclasses import dataclass
from typing import List

from saltgang import args as argsmod
from saltgang import logger as loggermod

_logger = logging.getLogger(__name__)


@dataclass(init=False)
class YttParams:
    main: pathlib.Path
    values: List[pathlib.Path]
    outpath: pathlib.Path
    basedir: pathlib.Path = None

    def __init__(self, main: str, values: List[str], outpath: str) -> None:
        self.main = pathlib.Path(main).resolve()
        self.values = [pathlib.Path(x).resolve() for x in values]
        self.outpath = pathlib.Path(outpath).resolve()


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
            _logger.fatal("{}".format(stderr.decode()))
        else:
            self.params.outpath.write_text(stdout.decode())


def main(args):
    Ytt()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    argsmod.add_common_args(parser)
    args = parser.parse_args()
    loggermod.setup_logging(args.loglevel)

    main(args)
