import argparse
import subprocess

import pytest

from saltgang import args as argsmod
from saltgang import encassist


@pytest.fixture
def my_parser():
    parser = argparse.ArgumentParser()
    argsmod.add_common_args(parser)
    encassist.add_arguments(parser)
    return parser


def test_no_config_causes_error(caplog, my_parser, tmp_path):
    args = my_parser.parse_args(["--sku", "macos", "--config-basedir", str(tmp_path)])
    encassist.main(args)
    assert "Error: Checking file" in caplog.text


def test_foo():
    def foo():
        cmd = ["ls", "/folder_does_not_exist"]
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        out, err = proc.communicate()
        return_code = proc.wait()

        ex = subprocess.CalledProcessError(return_code, cmd=cmd, output=out)
        ex.stdout, ex.stderr = out, err

        if proc.returncode not in [0]:
            raise ex

    with pytest.raises(subprocess.CalledProcessError):
        foo()


@pytest.mark.parametrize(
    "params",
    [
        [],
        ["--sku", "MACOS"],
        ["--sku", "Macos"],
        ["-vv1", "--sku", "macos"],
        ["--sku", "macos", "--sku", "avid"],
        ["-vv1", "--sku", "macos", "--sku", "macos"],
        ["-vv1", "--sku", "macos", "--sku", "avid"],
    ],
)
def test_incorrect_args_causes_systemexit(my_parser, params):
    with pytest.raises(SystemExit):
        my_parser.parse_args(params)


@pytest.mark.parametrize(
    "params",
    [
        ["--sku", "macos", "--sku", "avid"],
    ],
)
def test_specifying_same_arg_twice_triggers_exception(my_parser, params):
    with pytest.raises(SystemExit):
        my_parser.parse_args(params)


def test_base_case_with_verbose_args(my_parser):
    args = my_parser.parse_args(["-vv", "--sku", "macos"])
    encassist.main(args)


def test_base_case(my_parser):
    args = my_parser.parse_args(["--sku", "macos"])
    encassist.main(args)
