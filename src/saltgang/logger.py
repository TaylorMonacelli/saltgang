import logging
import sys


def setup_logging(loglevel):
    logformat = "{%(filename)s:%(lineno)d} %(levelname)s - %(message)s"
    logging.basicConfig(
        level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
    )
