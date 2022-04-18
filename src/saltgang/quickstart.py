import argparse
import hashlib
import logging
import pathlib
import re
import shutil
import string
import subprocess
import sys
import tempfile
import zipfile

import furl
import gdown
import magic
import pdfminer.high_level
import yaml

from saltgang import args as argsmod
from saltgang import common
from saltgang import logger as loggermod

"""
Expected

output-quickstart-guide/staging
`-- latest
    |-- macos
    |   `-- quickstart.pdf
    `-- win
        |-- universal
        |   `-- quickstart.pdf
        `-- avid
            `-- quickstart.pdf

5 directories, 3 files
"""


def add_arguments(parser):
    parser.add_argument("--force-fetch", default=False, action="store_true")
    parser.add_argument("--upload", default=False, action="store_true")


def add_parser(subparsers):
    parser = subparsers.add_parser(
        "quickstart",
        help="fetch and upload quickstart pdfs",
        aliases=["quick"],
    )
    add_arguments(parser)


def main(args):
    logger = logging.getLogger(__name__)

    project_path = common.project_path()

    encassist_path = project_path / "installer/encassist.yml"

    if not encassist_path.exists():
        logger.warning(f"Can't find {encassist_path}")
        sys.exit(-1)

    with open(encassist_path, "r") as f:
        encassist = yaml.safe_load(f.read())

    try:
        lst = list(
            filter(lambda record: record["name"] == "quickstartguide-url", encassist)
        )

        found = lst[0]
    except IndexError:
        logger.exception(f"I can't find key quickstartguide-url in {encassist_path}")
        raise

    source = furl.furl(found["source_url"]["latest"])
    deploy_path = found["deploy_path"]

    keep_chars = string.ascii_letters + string.digits
    p1 = re.sub(f"[^{''.join(keep_chars)}]", "-", deploy_path).lower().replace(" ", "-")
    p1 = re.sub("-{2,}", "-", p1)
    logger.debug("p1: {}".format(p1))

    assert source.url
    assert deploy_path

    logger.debug("found url to fetch {}".format(source.url))

    scratch = pathlib.Path("output-quickstart-guide")
    scratch = scratch.resolve()
    pathlib.Path.mkdir(scratch, parents=True, exist_ok=True)

    step10_dir = scratch / "step10"
    step20_dir = scratch / "step20"
    step30_dir = scratch / "step30"
    step40_dir = scratch / "staging"

    digest = hashlib.sha256(source.url.encode()).hexdigest()

    logger.debug(f"sha256 of url {source.url} is {digest}")

    step10_path = step10_dir / digest
    step20_path = step20_dir / p1
    step30_path = step30_dir / p1
    step40_path = step40_dir
    quickstart_path = step30_path / "quickstart.pdf"

    pathlib.Path.mkdir(step10_dir, parents=True, exist_ok=True)
    pathlib.Path.mkdir(step20_dir, parents=True, exist_ok=True)
    pathlib.Path.mkdir(step30_dir, parents=True, exist_ok=True)
    pathlib.Path.mkdir(step40_dir, parents=True, exist_ok=True)
    pathlib.Path.mkdir(step20_path, parents=True, exist_ok=True)
    pathlib.Path.mkdir(step30_path, parents=True, exist_ok=True)

    tmp_path = pathlib.Path(tempfile.gettempdir()) / step10_path.name
    tmp_path.unlink(missing_ok=True)

    if not step10_path.exists() or args.force_fetch:
        gdown.download(source.url, str(tmp_path), quiet=True)
        tmp_path.rename(step10_path)

    file_type = magic.from_file(str(step10_path), mime=True)

    logger.debug(f"file {str(step10_path)} is type {file_type}")

    if file_type == "application/zip":
        with zipfile.ZipFile(step10_path, "r") as zip_ref:
            zip_ref.extractall(step20_path)

        pdfs = list(step20_path.glob("**/*.pdf"))

        pdf = None
        if len(pdfs) == 1:
            pdf = pdfs[0].resolve()
        else:
            preview = source.args.get("preview", None)
            file_subpath = source.args.get("file_subpath", None)

            pdf = pathlib.Path(preview if preview else file_subpath)

        assert pdf

        extracted_pdf_path = step20_path / pdf

        logger.debug(f"{pdf=}")
        logger.debug(f"{step20_path=}")
        logger.debug(f"{extracted_pdf_path=}")

        logger.debug(f"copying {extracted_pdf_path} to {quickstart_path}")
        shutil.copy(extracted_pdf_path, quickstart_path)

    elif file_type == "application/pdf":
        shutil.copy(step10_path, quickstart_path)

    else:
        logger.exception(f"Can't handle {step10_path}.  Filetype: {file_type}")
        raise ValueError(step10_path)

    assert quickstart_path.exists()

    assert "s3://streambox-spectra/" in str(deploy_path)

    x = str(deploy_path).replace("s3://streambox-spectra/", "")
    staging = step40_dir / x

    logger.debug(f"{staging=}")

    if staging.exists():
        logger.debug(f"removing pre-existing file {staging}")

    staging.unlink(missing_ok=True)

    pathlib.Path.mkdir(staging.parent, parents=True, exist_ok=True)
    logger.debug(f"will copy {quickstart_path} to {staging}")
    shutil.copy(quickstart_path, staging)

    latest = step40_path / "latest"

    pdfs = list(latest.glob("**/*.pdf"))

    for pdf in pdfs:
        logger.debug(f"I see {pdf} is present")

    logging.getLogger("pdfminer").setLevel(logging.ERROR)
    text = pdfminer.high_level.extract_text(pdf)
    logger.debug(
        "I see 'Streambox' in {}, so I take that to mean this pdf is readable".format(
            pdf
        )
    )

    assert "Streambox" in text

    # ancient installers link to pdf named "quickstart.pdf". The names
    # have since been changed, but we need to push new quickstarts to
    # old pdf name to support old installers.
    old_pdf = staging.parent / "quickstart.pdf"
    logger.debug(f"copying {pdf} to {old_pdf}")
    shutil.copy(pdf, old_pdf)

    if args.upload:
        sync = [
            "aws",
            "s3",
            "sync",
            str(latest),
            "s3://streambox-spectra/latest",
            "--grants",
            "read=uri=http://acs.amazonaws.com/groups/global/AllUsers",
            "--region",
            "us-west-2",
            "--profile",
            "spectra_deploy",
        ]

        logger.debug(sync)

        process = subprocess.Popen(
            sync,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        stdout, stderr = process.communicate()

        logger.debug(stdout.decode())

        if stderr:
            logger.warning("{}".format(stderr.decode()))


add_parser(argsmod.subparsers)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    add_arguments(parser)
    argsmod.add_common_args(parser)
    args = parser.parse_args()
    loggermod.setup_logging(args.loglevel)

    main(args)
