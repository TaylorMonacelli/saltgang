import argparse

import pytest

from saltgang import args as argsmod
from saltgang import meta


@pytest.fixture
def my_parser():
    parser = argparse.ArgumentParser()
    argsmod.add_common_args(parser)
    meta.add_arguments(parser)
    return parser


@pytest.mark.skip(
    reason="meta module requires I cd to spectra_installer project dir, not good for testing"
)
def test(my_parser):
    args = my_parser.parse_args([])
    meta.main(args)
