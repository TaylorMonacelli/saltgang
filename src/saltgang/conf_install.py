import logging
import pathlib
import shutil

import pkg_resources
import platformdirs

_logger = logging.getLogger(__name__)


def main():
    package = __name__.split(".")[0]
    appname = package
    appauthor = ""
    basedir = pathlib.Path(platformdirs.user_data_dir(appname, appauthor))
    deployed_conf = basedir / "config.yml"
    deployed_conf.parent.mkdir(parents=True, exist_ok=True)
    PACKAGE_CONF_DIR = pathlib.Path(pkg_resources.resource_filename(package, "conf/"))
    src = PACKAGE_CONF_DIR / "config.yml"
    dst = deployed_conf
    _logger.debug(f"copying {src} to {dst}")
    if not deployed_conf.exists():
        shutil.copy(str(src), str(deployed_conf))
    return deployed_conf
