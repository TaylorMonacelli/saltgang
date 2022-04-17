import argparse
import logging

from omegaconf import OmegaConf

from saltgang import args as argsmod
from saltgang import conf as confmod
from saltgang import logger as loggermod
from saltgang import ytt as yttmod

_logger = logging.getLogger(__name__)


def add_arguments(parser):
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
    ytt_params = None
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

    conf_path = confmod.get_deployed_conf()
    if not conf_path.exists():
        confmod.main(args)

    _logger.info(f"reading {conf_path}")
    conf = OmegaConf.load(conf_path)

    values = conf.sku[sku].value_paths
    outpath = conf.sku[sku].outpath

    b = args.config_basedir if args.config_basedir else conf.common.configdir
    conf.common.configdir = b

    ytt_params = yttmod.YttParams(
        main=conf.common.main,
        values=values,
        outpath=outpath,
    )

    _logger.debug(ytt_params)
    ytt = yttmod.Ytt(ytt_params)

    if not yttmod.Ytt.check_installed():
        _logger.fatal("Can't find ytt")
        raise FileNotFoundError("Can't find ytt")

    ytt.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    argsmod.add_common_args(parser)
    add_arguments(parser)
    args = parser.parse_args()
    loggermod.setup_logging(args.loglevel)

    main(args)
