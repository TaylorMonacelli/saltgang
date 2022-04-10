import logging
import pathlib


def project_path():
    logger = logging.getLogger(__name__)

    p1 = pathlib.Path("/")
    cwd = pathlib.Path.cwd()

    logger.debug("starting search for git project at {}".format(cwd))

    for i, part in enumerate(cwd.parts):
        if i == 0:
            continue
        p1 = p1 / part

        if part == "spectra_installer":
            logger.debug("found project at {}".format(p1))
            break

    return p1
