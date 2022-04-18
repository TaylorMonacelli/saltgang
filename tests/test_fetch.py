import argparse

import pytest

from saltgang import args as argsmod
from saltgang import fetch


@pytest.fixture
def my_parser():
    parser = argparse.ArgumentParser()
    argsmod.add_common_args(parser)
    fetch.add_arguments(parser)
    return parser


@pytest.mark.skip(
    reason="fetch module requires I cd to spectra_installer project dir, not good for testing"
)
def test(my_parser):
    parser = argparse.ArgumentParser()
    argsmod.add_common_args(parser)
    fetch.add_arguments(parser)
    args = my_parser.parse_args(
        ["https://www.dropbox.com/s/zirk55k8ty0dy1i/Spectra.prm.2.0.4.zip?dl=0"]
    )
    fetch.main(args)
