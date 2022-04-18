import argparse

from saltgang import args as argsmod
from saltgang import meta


def test():
    parser = argparse.ArgumentParser()
    argsmod.add_common_args(parser)
    meta.add_arguments(parser)
    args = parser.parse_args(
        ["https://www.dropbox.com/s/zirk55k8ty0dy1i/Spectra.prm.2.0.4.zip?dl=0"]
    )
    meta.main(args)
