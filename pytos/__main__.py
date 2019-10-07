import sys

from pytos.parser import argparse
from pytos.rc.collect import initialize_context


def main():
    rc, parser = argparse.get_parser()
    args = parser.parse_args()
    runner = rc[args.CMD]

    err = runner.parse_args(args.ARG)
    if err != 0:
        return err

    context, err = initialize_context(args.CONFIG_FILE)
    if err != 0:
        return err

    return runner.run(context)


if __name__ == '__main__':
    sys.exit(main())
