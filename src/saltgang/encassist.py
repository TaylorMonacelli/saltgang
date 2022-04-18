import argparse
import logging

from omegaconf import OmegaConf

from saltgang import args as argsmod
from saltgang import conf as confmod
from saltgang import logger as loggermod
from saltgang import ytt as yttmod

_logger = logging.getLogger(__name__)


class Highlander(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if getattr(namespace, self.dest, None) is not None:
            raise argparse.ArgumentError(self, "There can be only one.")
        setattr(namespace, self.dest, values)


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
        "--outpath",
        help="provide the path to where to write the resulting encassist yaml file",
    )
    parser.add_argument(
        "--sku",
        help="",
        action=Highlander,
        choices=["macos", "linux", "avid", "universal"],
        required=True,
    )


def add_parser(subparsers):
    parser = subparsers.add_parser(
        "encassist",
        aliases=["enc"],
        help="using ytt, merge specific encassist variables into global encassist.yml",
    )
    add_arguments(parser)


def main(args):
    conf_path = confmod.get_deployed_conf()
    if not conf_path.exists():
        confmod.install_conf(conf_path)
    _logger.info(f"reading {conf_path}")
    conf = OmegaConf.load(conf_path)
    values = conf.sku[args.sku].value_paths

    o = args.outpath if args.outpath else conf.sku[args.sku].outpath
    conf.sku[args.sku].outpath = o

    b = args.config_basedir if args.config_basedir else conf.common.configdir
    conf.common.configdir = b

    ytt_params = yttmod.YttParams(
        main=conf.common.main,
        values=values,
        outpath=conf.sku[args.sku].outpath,
    )
    print(ytt_params)

    _logger.debug(ytt_params)
    ytt = yttmod.Ytt(ytt_params)

    if not yttmod.Ytt.check_installed():
        _logger.fatal("Can't find ytt")
        raise FileNotFoundError("Can't find ytt")

    ytt.run()


add_parser(argsmod.subparsers)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    argsmod.add_common_args(parser)
    add_arguments(parser)
    args = parser.parse_args()
    loggermod.setup_logging(args.loglevel)

    main(args)
