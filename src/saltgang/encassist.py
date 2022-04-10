import argparse
import logging
import pathlib
import subprocess

from saltgang import logger as loggermod
from saltgang import ytt

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
        "--config_dir",
        required=True,
        help="provide the base direct path to encassist yaml files, eg --config_dir tmp",
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


class Encassist:
    # pylint: disable=line-too-long
    """
    ytt -f encassist/encassist.yml -f encassist/values/macos/*.yml >encassist.yml
    ytt -f encassist/encassist.yml -f encassist/values/win/*.yml -f encassist/values/win/avid/*.yml >encassist.yml
    ytt -f encassist/encassist.yml -f encassist/values/win/*.yml -f encassist/values/win/universal/*.yml >encassist.yml
    """

    def __init__(self, dirconfig: str, ytt: ytt.YttParams):
        self.config_basedir = dirconfig
        self.main_path = ytt.main
        self.inlist = ytt.values
        self.outpath = ytt.out
        # self.initialze()

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
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        stdout, stderr = process.communicate()
        if stderr:
            _logger.warning("{}".format(stderr.decode()))
        else:
            self.outpath.write_text(stdout.decode())


def main(args):
    if not ytt.Ytt().installed:
        _logger.fatal("Can't find ytt")
        raise FileNotFoundError("Can't find ytt")

    basedir = pathlib.Path(args.config_dir)

    if args.macos:
        ytt_params = ytt.YttParams(
            main=basedir / "encassist/encassist.yml",
            values=[basedir / "encassist/values/macos/values.yml"],
            out="macos.yml",
        )

    elif args.win_avid:
        ytt_params = ytt.YttParams(
            main=basedir / "encassist/encassist.yml",
            values=[
                basedir / "encassist/values/win/values.yml",
                basedir / "encassist/values/win/avid/values.yml",
            ],
            out="avid.yml",
        )

    elif args.linux:
        ytt_params = ytt.YttParams(
            main=basedir / "encassist/encassist.yml",
            values=[basedir / "encassist/values/linux/values.yml"],
            out="linux.yml",
        )

    elif args.win_universal:
        ytt_params = ytt.YttParams(
            main=basedir / "encassist/encassist.yml",
            values=[
                basedir / "encassist/values/win/values.yml",
                basedir / "encassist/values/win/universal/values.yml",
            ],
            out="universal.yml",
        )

    else:
        raise ValueError("encassist: no args")

    enc = Encassist(args.config_dir, ytt_params)
    enc.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    add_arguments(parser)
    args = parser.parse_args()
    loggermod.setup_logging(args.loglevel)

    main(args)
