import argparse
import datetime
import glob
import hashlib
import logging
import pathlib
import shutil
import sys
import tempfile
import zipfile

import requests

from saltgang import args as argsmod
from saltgang import logger as loggermod


def add_arguments(parser):
    parser.add_argument("url", help="url to download")


def add_parser(subparsers):
    parser = subparsers.add_parser(
        "down",
        help=(
            "download url and expand (if zip) into cwd.  Example: {cmd} down "
            "https://www.dropbox.com/s/zirk55k8ty0dy1i/Spectra.prm.2.0.4.zip?dl=0"
        ),
    )
    add_arguments(parser)


def validate_cwd():
    d1 = pathlib.Path.cwd()
    d1a = d1.name.lower()
    d2 = d1.parent.name.lower()

    if d1a != "app" or d2 != "spectra_installer":
        msg = "cd to 'spectra_installer/app' directory before running this"
        logger = logging.getLogger(__name__)
        logger.fatal(msg)
        sys.exit(-1)


class MyURL:
    def __init__(self, url):
        clean = f"{url.rstrip('?dl=0').rstrip('?dl=1')}?dl=1"  # cleaned url
        self.url = url
        self.clean = clean
        self.clean2 = clean.rstrip("?dl=1")
        self.hash = hashlib.sha256(clean.encode())


class Helper:
    def __init__(self, url: str):
        self.logger = logging.getLogger(__name__)
        url = MyURL(url)

        p1 = tempfile.gettempdir()
        root = pathlib.Path(p1) / "spectra"
        cache_dir = root / url.hash.hexdigest()
        expanded_dir = root / "expanded"
        original_dir = cache_dir / "original"
        cache = original_dir / pathlib.Path(url.clean2).name

        self.url = url
        self.cache = cache
        self.original_dir = original_dir
        self.cache_dir = cache_dir
        self.expanded_dir = expanded_dir

    def download(self):
        validate_cwd()

        app_dir = pathlib.Path(".")

        self._setup_dir()
        self.fetch()
        self.expand()
        self._overwrite(app_dir)

    def _overwrite(self, app_dir):
        g1 = self.expanded_dir / "*"

        for file_name in glob.glob(str(g1)):
            new_path = app_dir / pathlib.Path(file_name).name
            shutil.copy(file_name, new_path)

    def fetch(self):
        if self.cache.exists():
            self.logger.debug(
                "using cached copy of {} from {}".format(self.url.url, self.cache)
            )

        if not self.cache.exists():
            r = requests.get(self.url.clean, allow_redirects=True)
            self.logger.debug("writing {} to cache {}".format(self.url.url, self.cache))
            open(self.cache, "wb").write(r.content)

    def expand(self):
        if pathlib.Path(self.cache).suffix.lower() != ".zip":
            self.logger.debug("copy {} to {}".format(self.cache, self.expanded_dir))
            shutil.copy(self.cache, self.expanded_dir)
        else:
            self.logger.debug(
                "expanding {} to {}".format(self.cache, self.expanded_dir)
            )
            with zipfile.ZipFile(self.cache, "r") as zipObj:
                zipObj.extractall(path=self.expanded_dir)

    def _setup_dir(self):
        timestamp = datetime.datetime.now().strftime("%s")

        t1 = f"{self.expanded_dir.name}_{timestamp}"
        tmp = self.expanded_dir.parent.resolve() / t1

        if self.expanded_dir.exists():
            self.expanded_dir.rename(tmp)

        def mkdir(_dir):
            pathlib.Path.mkdir(_dir, parents=True, exist_ok=True)

        self.logger.debug("mkdir {}".format(self.cache_dir))

        mkdir(self.cache_dir)
        mkdir(self.expanded_dir)
        mkdir(self.original_dir)


def main(args):
    validate_cwd()
    Helper(args.url).download()


add_parser(argsmod.subparsers)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    argsmod.add_common_args(parser)
    add_arguments(parser)
    args = parser.parse_args()
    loggermod.setup_logging(args.loglevel)

    main(args)
