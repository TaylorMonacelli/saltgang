import argparse
import os
import pathlib
import subprocess
import sys

import pytest

from saltgang import args as argsmod
from saltgang import encassist


@pytest.fixture
def my_parser():
    parser = argparse.ArgumentParser()
    argsmod.add_common_args(parser)
    encassist.add_arguments(parser)
    return parser


def test_no_config_causes_error5(caplog, my_parser, tmp_path):
    args = my_parser.parse_args(
        ["--sku", "macos", "--config-basedir", str(tmp_path.parent)]
    )
    encassist.main(args)
    assert "Error: Checking file" in caplog.text


def foo():
    cmd = ["ls", "/tmp1"]
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    out, err = proc.communicate()

    return_code = proc.poll()
    out = out.decode(sys.stdin.encoding)
    err = err.decode(sys.stdin.encoding)

    ex = subprocess.CalledProcessError(return_code, cmd=cmd, output=out)
    ex.stdout, ex.stderr = out, err

    if proc.returncode not in [0]:
        raise ex


def test_foo(capfd):
    with pytest.raises(subprocess.CalledProcessError):
        foo()  # Writes "Hello World!" to stdout


@pytest.mark.skip(reason="not sure how to handle this one")
def test_no_config_causes_error1(capsys, my_parser, tmp_path):
    p = pathlib.Path(tmp_path.parent)
    os.chdir(p)
    args = my_parser.parse_args(["--sku", "macos"])
    with pytest.raises(subprocess.CalledProcessError):
        encassist.main(args)


@pytest.mark.skip(reason="not sure how to handle this one")
def test_no_config_causes_error(capsys, my_parser, tmp_path):
    p = pathlib.Path(tmp_path.parent)
    os.chdir(p)
    args = my_parser.parse_args(["--sku", "macos"])
    encassist.main(args)
    captured = capsys.readouterr()
    assert "Error" in captured.err


def test_empty_args_causes_systemexit(my_parser):
    with pytest.raises(SystemExit):
        my_parser.parse_args([])


def test_incorrect_args_causes_systemexit_2(my_parser):
    with pytest.raises(SystemExit):
        my_parser.parse_args(["--sku", "MACOS"])


def test_incorrect_args_causes_systemexit(my_parser):
    with pytest.raises(SystemExit):
        my_parser.parse_args(["-vv1", "--sku", "macos"])


def test_too_many_args_causes_systemexit(my_parser):
    with pytest.raises(SystemExit):
        my_parser.parse_args(["-vv1", "--sku", "macos", "--sku", "macos"])
    with pytest.raises(SystemExit):
        my_parser.parse_args(["-vv1", "--sku", "macos", "--sku", "avid"])


def test2_base_case_with_verbose_args(my_parser):
    args = my_parser.parse_args(["-vv", "--sku", "macos"])
    encassist.main(args)


def test_base_case(my_parser):
    args = my_parser.parse_args(["--sku", "macos"])
    encassist.main(args)
