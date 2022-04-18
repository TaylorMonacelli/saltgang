import argparse

from saltgang import encassist


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--sku",
        help="",
        choices=["macos", "linux", "avid", "universal"],
        required=True,
    )
    parser.add_argument(
        "--outpath",
        help="provide the path to where to write the resulting encassist yaml file",
    )

    args = parser.parse_args(args)
    print(args)
    return args


def test():
    # parser = parse_args(sys.argv[1:])
    args = parse_args(["--sku", "macos"])
    encassist.main(args)
