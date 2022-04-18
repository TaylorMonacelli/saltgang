import argparse
import dataclasses
import logging
import pathlib
import sys
import typing

import jinja2
import pkg_resources
import xdgappdirs
import yaml

from saltgang import args as argsmod
from saltgang import common
from saltgang import logger as loggermod

_logger = logging.getLogger(__name__)


def add_arguments(parser):
    parser.add_argument("-yp", "--yaml-path", required=False)
    parser.add_argument("--outpath", required=False)

    parser_group = parser.add_mutually_exclusive_group()
    parser_group.add_argument(
        "--view4", const="view4", action="store_const", dest="view"
    )
    parser_group.add_argument(
        "--view5", const="view5", action="store_const", dest="view"
    )
    parser_group.add_argument("--go", const="go", action="store_const", dest="view")
    parser_group.add_argument("--c", const="c", action="store_const", dest="view")
    parser_group.add_argument(
        "--ini-check", const="ini_check", action="store_const", dest="view"
    )
    parser_group.add_argument("--ini", const="ini", action="store_const", dest="view")
    parser_group.add_argument("--ini2", const="ini2", action="store_const", dest="view")
    parser_group.add_argument(
        "--view7", const="view7", action="store_const", dest="view"
    )
    parser.set_defaults(view="ini")


def add_parser(subparsers):
    parser = subparsers.add_parser(
        "config",
        help="config help",
        aliases=["settings"],
    )
    add_arguments(parser)


class Setting:
    def __init__(self, iterable=(), **kwargs):
        self.__dict__.update(iterable, **kwargs)

    def quote(self, val):
        if " " in str(val):
            return f'"{val}"'
        return val


@dataclasses.dataclass
class Settings:
    _list: typing.List[Setting] = dataclasses.field(default_factory=list)
    yaml_path: pathlib.Path = pathlib.Path("")

    @classmethod
    def config_path(cls):
        appname = __name__
        appauthor = "Streambox"

        _str = xdgappdirs.user_config_dir(appname, appauthor)
        _logger.debug("{} will look for config in path {}".format(__name__, _str))
        return pathlib.Path(_str)

    @classmethod
    def from_file(cls, yaml_path):
        logger = logging.getLogger(__name__)
        if not yaml_path:
            yaml_path = common.project_path() / "installer" / "encassist.yml"

        _list = []
        if not yaml_path.exists():
            logger.warning(f"{yaml_path} does not exist")
            sys.exit(-1)
        with open(yaml_path, "r") as stream:
            for dct in yaml.safe_load(stream):
                setting = Setting(dct)
                _list.append(setting)
        return Settings(_list)

    def view(self, name):
        r = self.tmpl_as_string(name)
        return jinja2.Template(r).render(settings=self._list)

    def tmpl_as_string(self, name):
        package = __name__.split(".")[0]
        TEMPLATES_PATH = pathlib.Path(
            pkg_resources.resource_filename(package, "templates/")
        )
        path = TEMPLATES_PATH / f"{name}.tmpl"
        return path.read_text()

    def __iter__(self):
        for setting in self._list:
            yield setting


def main(args):
    yaml_path = pathlib.Path(args.yaml_path) if args.yaml_path else None
    settings = Settings.from_file(yaml_path)
    rendered = settings.view(args.view)
    _logger.debug(f"rendered view {args.view} to stdout")
    print(rendered)
    if args.outpath:
        outpath = pathlib.Path(args.outpath)
        _logger.debug(f"rendered view {args.view} to {outpath}")
        outpath.write_text(rendered)


add_parser(argsmod.subparsers)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    add_arguments(parser)
    argsmod.add_common_args(parser)
    args = parser.parse_args()
    loggermod.setup_logging(args.loglevel)

    main(args)
