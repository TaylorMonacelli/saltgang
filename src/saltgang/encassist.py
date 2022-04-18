import argparse
import logging

from omegaconf import OmegaConf

from saltgang import args as argsmod
from saltgang import conf as confmod
from saltgang import logger as loggermod
from saltgang import ytt as yttmod

_logger = logging.getLogger(__name__)


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

    _logger.debug(ytt_params)
    ytt = yttmod.Ytt(ytt_params)

    if not yttmod.Ytt.check_installed():
        _logger.fatal("Can't find ytt")
        raise FileNotFoundError("Can't find ytt")

    ytt.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    argsmod.add_common_args(parser)
    # add_arguments(parser)
    args = parser.parse_args()
    loggermod.setup_logging(args.loglevel)

    main(args)
