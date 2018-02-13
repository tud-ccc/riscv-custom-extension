#!/usr/bin/env python

import argparse
import logging
import os
from parser.parser import Parser
import sys

logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger(__name__)


def main():
    '''
    Main function.
    '''

    # argparsing
    parser = argparse.ArgumentParser(
        prog='modelparser',
        description='Parse reference implementations of custom extension ' +
        'models.')

    parser.add_argument('-v',
                        '--verbosity',
                        default=0,
                        action='count',
                        help='Increase output verbosity.')
    parser.add_argument('-b',
                        '--build',
                        action='store_true',
                        help='If set, Toolchain and Gem5 will be ' +
                        'rebuild.')
    parser.add_argument('-m',
                        '--model',
                        type=str,
                        default=os.path.join(
                            os.path.dirname(__file__),
                            'extensions',
                            'test.cc'),
                        help='Reference implementation')

    args = parser.parse_args()

    logger.setLevel(50 - 10 * args.verbosity)

    Parser(args)


if __name__ == '__main__':
    main()
