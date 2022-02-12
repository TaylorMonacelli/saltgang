import logging

filename = f"{__name__.split('.')[0]}.log"

# pylint: disable=line-too-long
format_fh = "[%(asctime)s] p%(process)s {%(filename)s:%(lineno)d} %(levelname)s - %(message)s"  # file
format_stream = "{%(filename)s:%(lineno)d} %(levelname)s - %(message)s"  # stream

formatter_fh = logging.Formatter(format_fh, "%Y-%m-%d %H:%M:%S %Z")  # add timezone
formatter_stream = logging.Formatter(format_stream)

fh = logging.FileHandler(filename)
stream = logging.StreamHandler()

fh.setFormatter(formatter_fh)
stream.setFormatter(formatter_stream)

fh.setLevel(logging.DEBUG)
stream.setLevel(logging.INFO)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

logger.addHandler(fh)
logger.addHandler(stream)
