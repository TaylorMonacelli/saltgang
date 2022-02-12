import argparse
import logging
import re
import subprocess

from saltgang import args as argsmod
from saltgang import logger as loggermod

_logger = logging.getLogger(__name__)


def add_arguments(parser):
    argsmod.add_common_args(parser)


class Ytt:
    def __init__(self):
        _logger.debug(f"creating instance of {type(self)}")
        self.installed = None
        self.check_installed()

    def check_installed(self):
        process = subprocess.Popen(
            "ytt version",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        try:
            stdout, stderr = process.communicate()
            if stderr:
                raise ValueError(stderr.decode())

            if not re.search(r"ytt version \d+\.\d+", stdout.decode()):
                raise ValueError("Can't find ytt installed")
            self.installed = True
        except ValueError as ex:
            self.logger.exception(ex)
            self.installed = False


def main(args):
    Ytt()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    add_arguments(parser)
    args = parser.parse_args()
    loggermod.setup_logging(args.loglevel)

    main(args)
