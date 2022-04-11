import argparse
import logging

from omegaconf import OmegaConf

from saltgang import conf_install
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
        "--config_basedir",
        required=True,
        help="provide the base direct path to encassist yaml files",
    )
    parser.add_argument(
        "--conf",
        help="path to config.yml",
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

    ytt_params = None

    if not args.conf:
        args.conf = conf_install.main()

    conf = OmegaConf.load(args.conf)
    conf.common.configdir = args.config_basedir

    values = None
    sku = None

    if args.macos:
        sku = "macos"

    elif args.win_avid:
        sku = "avid"

    elif args.linux:
        sku = "linux"

    elif args.win_universal:
        sku = "universal"

    else:
        raise ValueError("encassist: no args")

    values = conf.sku[sku].value_paths
    outpath = conf.sku[sku].outpath

    ytt_params = yttmod.YttParams(
        main=conf.common.main,
        values=values,
        outpath=outpath,
    )

    ytt_params.set_basedir(conf.common.configdir)
    ytt = yttmod.Ytt(ytt_params)
    ytt.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    add_arguments(parser)
    args = parser.parse_args()
    loggermod.setup_logging(args.loglevel)

    main(args)
