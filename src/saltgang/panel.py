"""
python when does module scoped variable get evaluated

python set module level variables

for file in zip.namelist():
    if file.startswith("dist/"):
        zip.extract(file, appdir)

python ZipFile extract different directory
python ZipFile extract subdirectory
python zipfile extractall remove path

ZipFile extract remove directorys


python type annotate return dict
typing.Dict[str, str]

python tarfile getmembers

python tarfile context manager

with contextlib.closing(tarfile.open('/dir/dir/dir.tar.gz', 'w:gz')) as fl:
    fl.add('/dir/dir/dir/', arcname = '/')


python tarfile walk extract

import tarfile,os
import sys
os.chdir("/tmp/foo")
tar = tarfile.open("test.tar")
for member in tar.getmembers():
    f=tar.extractfile(member)
    content=f.read()
    print "%s has %d newlines" %(member, content.count("\n"))
    print "%s has %d spaces" % (member,content.count(" "))
    print "%s has %d characters" % (member, len(content))
    sys.exit()
tar.close()

tf = tarfile.open("samples.tar.gz")
print tf.next().name
print tf.next().name
print tf.next().name
print tf.next()



python tarfile

if fname.endswith("tar.gz"):
    tar = tarfile.open(fname, "r:gz")
    tar.extractall()
    tar.close()
elif fname.endswith("tar"):
    tar = tarfile.open(fname, "r:")
    tar.extractall()
    tar.close()

"""

import argparse
import logging
import pathlib
import shutil
import subprocess
import sys
import typing
import zipfile

import magic

from saltgang import args as argsmod
from saltgang import common
from saltgang import logger as loggermod

this = sys.modules[__name__]
this.project_path = None


def add_arguments(parser):
    pass


def add_parser(subparsers):
    parser = subparsers.add_parser(
        "panel",
        help="extract latest ECP_win32_*.zip",
        aliases=["ecp"],
    )
    add_arguments(parser)


def get_changed_or_added(tracking_path: pathlib.Path) -> typing.Dict[str, list]:
    logger = logging.getLogger(__name__)

    def doit(cmd):
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        logger.debug(" ".join([str(i) for i in cmd]))

        stdout, stderr = process.communicate()

        if stderr:
            logger.error(stderr.decode())
            sys.exit(-1)

        paths = []
        for path_str in stdout.decode().splitlines():
            if not path_str:
                continue

            path = this.project_path / path_str
            path = path.resolve()
            logger.debug(f"{path=}")
            paths.append(path)

        return paths

    tracking_path = this.project_path / "installer/other/tracking-upstream"

    paths = {
        "untracked": [],
        "changed": [],
    }

    cmd = [
        "git",
        "--git-dir",
        this.project_path / ".git",
        "--work-tree",
        this.project_path,
        "diff",
        "--pretty=",
        "--name-only",
        tracking_path,
    ]

    paths["changed"].append(doit(cmd))

    cmd = [
        "git",
        "--git-dir",
        this.project_path / ".git",
        "--work-tree",
        this.project_path,
        "ls-files",
        "--others",
        "--exclude-standard",
        tracking_path,
    ]

    paths["untracked"].append(doit(cmd))

    return paths


def extract(path_src=None, extract_to_dir=None):
    logger = logging.getLogger(__name__)

    file_type = magic.from_file(str(path_src), mime=True)
    logger.debug(f"{path_src} is of type {file_type}")

    # https://stackoverflow.com/a/6086722/1495086

    # FIXME: don't assume xzip file is tar

    def expunge(path: pathlib.Path):
        tmp = pathlib.Path("/tmp") / path.name
        logger.debug(f"moving {path} to {tmp}")
        path.rename(tmp)

    if file_type == "application/x-gzip":
        raise ValueError(f"not prepared to handle files like {path_src}")
        # with contextlib.closing(tarfile.open(str(path_src), "r:gz")) as fl:
        #     for member in fl.getmembers():
        #         logger.debug(f"member: {member}")
        #         f1 = fl.extractfile(member)
        #         # source = f1.read()
        #         # target = extract_to_dir / member.name
        #         # logger.debug(f"extract {membe.name} to {target}")
        #         # with source, target:
        #         #     shutil.copyfileobj(source, target)
        # expunge(path_src)

    elif file_type == "application/zip":
        with zipfile.ZipFile(path_src) as zip_file:
            for member in zip_file.namelist():
                path = pathlib.Path(member)

                if path.is_dir():
                    continue

                # copy file (taken from zipfile's extract)
                source = zip_file.open(member)
                target = open(extract_to_dir / path.name, "wb")
                with source, target:
                    shutil.copyfileobj(source, target)
        expunge(path_src)

    else:
        logger.exception(path)
        raise ValueError("I don't know how to extract {path}")


def main(args):
    logger = logging.getLogger(__name__)

    this.project_path = common.project_path()

    root = pathlib.Path("~/Downloads").expanduser()

    logger.debug(f"searching for files in {root}")

    appdir = pathlib.Path("~/pdev/streambox/spectra_installer/app").expanduser()
    logger.debug(f"appdir: {appdir}")

    records = []

    myglob = "ECP*.zip"
    for path in list(root.glob(myglob)):
        record = {"mtime": int(path.stat().st_mtime), "path": path}
        records.append(record)

    # myglob = "ECP*.tgz"
    # for path in list(root.glob(myglob)):
    #     record = {"mtime": path.stat().st_mtime, "path": path}
    #     records.append(record)

    logger.debug(f"{len(records)} candidates for glob {root}/{myglob}")

    # most recent mtim is winner, FIXME: compare versions instead
    records = sorted(records, key=lambda rec: rec["mtime"], reverse=True)

    logger.debug(records)

    if not records:
        logger.warning("existing, no candidates")
        sys.exit(-1)

    recent = records[0]
    zip_path = recent["path"]

    logger.info(f"using {zip_path}")

    tracking_path = this.project_path / "installer/other/tracking-upstream"

    extract(path_src=zip_path, extract_to_dir=tracking_path)
    paths = get_changed_or_added(tracking_path)

    changed = paths["changed"]
    untracked = paths["untracked"]

    all_paths = []
    all_paths.extend(*changed)
    all_paths.extend(*untracked)

    logger.debug(f"{all_paths=}")

    for path in all_paths:
        shutil.copy(path, appdir / path.name)


add_parser(argsmod.subparsers)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    argsmod.add_common_args(parser)
    add_arguments(parser)
    args = parser.parse_args()
    loggermod.setup_logging(args.loglevel)

    main(args)
