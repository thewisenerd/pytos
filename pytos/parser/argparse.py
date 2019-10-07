from argparse import ArgumentParser

from pytos.rc import collect


def get_parser():
    parser = ArgumentParser()
    rc = collect.collect()
    parser.add_argument('CMD', help='command to run', choices=rc.keys())
    parser.add_argument('ARG', help='arguments for command', nargs='*')
    parser.add_argument('-c', '--config-file', dest='CONFIG_FILE', default='config.toml')
    return rc, parser
