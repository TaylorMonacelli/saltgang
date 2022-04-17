import argparse
import hashlib
import logging
import pathlib
import shutil

import pkg_resources
import platformdirs

from saltgang import args as argsmod
from saltgang import logger as loggermod

_logger = logging.getLogger(__name__)

# FIXME: is there a better way other than whyat i've done here?
# package = __name__.split(".")[0]
# vs
# hardcoding package = "saltgang"
# otherwise, doing this:
# python -m saltgang.conf -vv
# would yield __main__
package = "saltgang"

appname = package
appauthor = ""


def is_different(conf1: pathlib.Path, conf2: pathlib.Path):
    def doit(path):
        digest = hashlib.md5(path.read_text().encode("utf-8")).hexdigest()
        _logger.debug(f"{path} has digest {digest}")
        return digest

    return doit(conf1) != doit(conf2)


def get_deployed_conf():
    dd = platformdirs.user_data_dir(appname, appauthor)
    path = pathlib.Path(dd) / get_package_conf().name
    return path


def get_package_conf():
    PACKAGE_CONF_DIR = pathlib.Path(pkg_resources.resource_filename(package, "conf/"))
    conf_fname = "config.yml"
    return PACKAGE_CONF_DIR / conf_fname


def install_conf(conf: pathlib.Path):
    conf.parent.mkdir(parents=True, exist_ok=True)
    src = get_package_conf()
    dst = conf
    if conf.exists():
        _logger.warning(f"{dst} already exists, aborting config overwrite.")
        return
    shutil.copy(str(src), str(conf))


def main(args):
    conf = get_deployed_conf()
    install_conf(conf)
    _logger.debug(conf)
    return conf


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    argsmod.add_common_args(parser)
    args = parser.parse_args()
    loggermod.setup_logging(args.loglevel)

    main(args)
