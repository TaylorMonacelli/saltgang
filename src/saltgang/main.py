import logging
import pathlib
import sys

from saltgang import args as argsmod
from saltgang import encassist, fetch, meta, mylogger, panel, quickstart
from saltgang import settings as settingsmod

__author__ = "Taylor Monacelli"
__copyright__ = "Taylor Monacelli"
__license__ = "MPL-2.0"

_logger = logging.getLogger(__name__)


def setup_logging(loglevel):
    logformat = "{%(filename)s:%(lineno)d} %(levelname)s - %(message)s"
    logging.basicConfig(
        level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
    )


def main(args):
    args = argsmod.parser.parse_args(args)
    setup_logging(args.loglevel)
    _logger.debug("Starting script...")

    if sys.version_info < (3, 7):
        raise Exception("need at least python3.7")

    if args.debug:
        mylogger.stream.setLevel(logging.DEBUG)

    logger = logging.getLogger(__name__)

    if args.command == "down":
        fetch.Helper(args.url).download()

    elif args.command in ["settings", "config"]:
        yaml_path = pathlib.Path(args.yaml_path) if args.yaml_path else None
        settings = settingsmod.Settings.from_file(yaml_path)
        rendered = settings.view(args.view)
        logger.debug(f"rendered view {args.view}")
        print(rendered)

    elif args.command == "url":
        meta.main()

    elif args.command in ["quick", "quickstart"]:
        quickstart.main(args=args)

    elif args.command in ["panel", "ecp"]:
        panel.main()

    elif args.command in ["enc", "encassist"]:
        encassist.main(args=args)

    else:
        raise ValueError("should not get here since required=True")

    _logger.info("Script ends here")


def run():
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
