import argparse

import pytest

from saltgang import args as argsmod
from saltgang import encassist


@pytest.fixture
def my_parser():
    parser = argparse.ArgumentParser()
    argsmod.add_common_args(parser)
    encassist.add_arguments(parser)
    return parser


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
