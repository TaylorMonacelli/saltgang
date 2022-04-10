import argparse
import logging
import pathlib

from saltgang import logger as loggermod
from saltgang import ytt as yttmod

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


def main(args):
    if not yttmod.Ytt.check_installed():
        _logger.fatal("Can't find ytt")
        raise FileNotFoundError("Can't find ytt")

    basedir = pathlib.Path(args.config_dir)
    ytt_params = None

    if args.macos:
        ytt_params = yttmod.YttParams(
            main=basedir / "encassist/encassist.yml",
            values=[basedir / "encassist/values/macos/values.yml"],
            outpath="macos.yml",
        )

    elif args.win_avid:
        ytt_params = yttmod.YttParams(
            main=basedir / "encassist/encassist.yml",
            values=[
                basedir / "encassist/values/win/values.yml",
                basedir / "encassist/values/win/avid/values.yml",
            ],
            outpath="avid.yml",
        )

    elif args.linux:
        ytt_params = yttmod.YttParams(
            main=basedir / "encassist/encassist.yml",
            values=[basedir / "encassist/values/linux/values.yml"],
            outpath="linux.yml",
        )

    elif args.win_universal:
        ytt_params = yttmod.YttParams(
            main=basedir / "encassist/encassist.yml",
            values=[
                basedir / "encassist/values/win/values.yml",
                basedir / "encassist/values/win/universal/values.yml",
            ],
            outpath="universal.yml",
        )

    else:
        raise ValueError("encassist: no args")

    ytt_params.set_basedir(basedir)
    ytt = yttmod.Ytt(ytt_params)
    ytt.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    add_arguments(parser)
    args = parser.parse_args()
    loggermod.setup_logging(args.loglevel)

    main(args)
