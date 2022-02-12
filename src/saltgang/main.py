import logging
import pathlib
import sys

from saltgang import args as argsmod
from saltgang import encassist, fetch
from saltgang import logger as loggermod
from saltgang import meta, panel, quickstart
from saltgang import settings as settingsmod

__author__ = "Taylor Monacelli"
__copyright__ = "Taylor Monacelli"
__license__ = "MPL-2.0"

_logger = logging.getLogger(__name__)


def main(args):
    args = argsmod.parser.parse_args(args)
    loggermod.setup_logging(args.loglevel)
    _logger.debug("Starting script...")

    if sys.version_info < (3, 7):
        raise Exception("need at least python3.7")

    if args.command == "down":
        fetch.Helper(args.url).download()

    elif args.command in ["settings", "config"]:
        yaml_path = pathlib.Path(args.yaml_path) if args.yaml_path else None
        settings = settingsmod.Settings.from_file(yaml_path)
        rendered = settings.view(args.view)
        _logger.debug(f"rendered view {args.view}")
        print(rendered)

    elif args.command == "url":
        meta.main(args)

    elif args.command in ["quick", "quickstart"]:
        quickstart.main(args)

    elif args.command in ["panel", "ecp"]:
        panel.main(args)

    elif args.command in ["enc", "encassist"]:
        encassist.main(args)

    else:
        raise ValueError("should not get here since required=True")

    _logger.info("Script ends here")


def run():
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
