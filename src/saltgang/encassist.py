import argparse
import logging
import pathlib
import subprocess
import typing
from dataclasses import dataclass, field
from typing import Any, List, Mapping

from saltgang import common
from saltgang import logger as loggermod
from saltgang import ytt

project_path = common.project_path()


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
    parser.add_argument(
        "--yaml-path",
        help="provide the path to encassist yaml file",
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--macos", action="store_true")
    group.add_argument("--linux", action="store_true")
    group.add_argument("--win-avid", action="store_true")
    group.add_argument("--win-universal", action="store_true")


def add_parser(subparsers):
    parser = subparsers.add_parser(
        "encassist",
        aliases=["enc"],
        help="using ytt, merge specific encassist variables into global encassist.yml",
    )
    add_arguments(parser)


class FileReadExeption(Exception):
    def __init__(self, value: str, message: str) -> None:
        self.value = value
        self.message = message
        super().__init__(message)


@dataclass
class FilesValidator:
    paths: typing.List[str] = field(default_factory=list)

    def are_readable(self):
        fails = []
        for _str in self.paths:
            path = pathlib.Path(_str)
            if not path.exist():
                fails.append(path)
                continue
            if path.read_text():
                fails.append(path)
                continue
        if fails:
            raise FileReadExeption(value=fails, message=f"Can't read paths {fails}")


@dataclass(init=False)
class ArgHolder:
    args: List[Any]
    kwargs: Mapping[Any, Any]

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


a = ArgHolder(1, 2, three=3)


class Encassist:
    # pylint: disable=line-too-long
    """
    ytt -f encassist/encassist.yml -f encassist/values/macos/*.yml >encassist.yml
    ytt -f encassist/encassist.yml -f encassist/values/win/*.yml -f encassist/values/win/avid/*.yml >encassist.yml
    ytt -f encassist/encassist.yml -f encassist/values/win/*.yml -f encassist/values/win/universal/*.yml >encassist.yml
    """

    def __init__(
        self, main_yaml: pathlib.Path, values_yaml: pathlib.Path, out_yaml: pathlib.Path
    ):
        self.main_path = common.project_path() / "installer/encassist/encassist.yml"
        self.inlist = values_yaml
        self.project_path = project_path
        self.main_path = common.project_path() / "installer/encassist/encassist.yml"
        self.outpath = out_yaml
        self.initialze()

    def initialze(self):
        if not self.main_path.exists():
            _logger.exception(f"Oops, I can't find {self.main_path}")
            raise ValueError(self.main_path)
        _logger.debug("{}".format(self.inlist))

    def run(self):
        cmd = [
            "ytt",
            "--output",
            "yaml",
            "-f",
            str(self.main_path),
        ]

        _logger.debug("inlist:{}".format(self.inlist))

        x = []
        for i in self.inlist:
            x.append("--file")
            x.append(str(i))

        cmd.extend(x)
        _logger.debug("cmd:{}".format(cmd))

        _logger.debug("running command {}".format(" ".join(cmd)))

        process = subprocess.Popen(
            cmd,
            cwd=str(project_path),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        stdout, stderr = process.communicate()
        if stderr:
            _logger.warning("{}".format(stderr.decode()))
        else:
            self.outpath.write_text(stdout.decode())


def main(args):
    _logger.debug(f"{project_path=}")

    if not ytt.Ytt().installed:
        _logger.fatal("Can't find ytt")
        raise ValueError("Can't find ytt")

    if args.macos:
        inpaths = [project_path / "installer/encassist/values/macos/values.yml"]

    elif args.win_avid:
        inpaths = [
            project_path / "installer/encassist/values/win/values.yml",
            project_path / "installer/encassist/values/win/avid/values.yml",
        ]

    elif args.linux:
        inpaths = [project_path / "installer/encassist/values/linux/values.yml"]

    elif args.win_universal:
        inpaths = [
            project_path / "installer/encassist/values/win/values.yml",
            project_path / "installer/encassist/values/win/universal/values.yml",
        ]

    else:
        raise ValueError("encassist: no args")

    outpath = project_path / "installer/encassist.yml"
    enc = Encassist(values_yaml=inpaths, out_yaml=outpath)
    enc.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    add_arguments(parser)
    args = parser.parse_args()
    loggermod.setup_logging(args.loglevel)

    main(args)
