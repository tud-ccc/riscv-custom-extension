#!/usr/bin/env python

import argparse
import logging
import logging.handlers
import os
from modelparsing.parser import Parser

# get root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

# # always write everything to the rotating log files
# if not os.path.exists('logs'):
#     os.mkdir('logs')
# log_file_handler = logging.handlers.TimedRotatingFileHandler(
#     'logs/args.log', when='M', interval=2)
# log_file_handler.setFormatter(logging.Formatter(
#     '%(asctime)s ' +
#     '[%(levelname)s]' +
#     '(%(name)s:%(funcName)s:%(lineno)d): %(message)s')
# )
# log_file_handler.setLevel(logging.DEBUG)
# root_logger.addHandler(log_file_handler)

# also log to the console at a level determined by the --verbose flag
console_handler = logging.StreamHandler()  # sys.stderr
# set later by set_log_level_from_verbose() in interactive sessions
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter(
    '[%(levelname)s](%(name)s): %(message)s'))
root_logger.addHandler(console_handler)

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
                        '--verbose',
                        default=0,
                        action='count',
                        help='Increase output verbosity.')
    parser.add_argument('-b',
                        '--build',
                        action='store_true',
                        help='If set, Toolchain and Gem5 will be ' +
                        'rebuild.')
    parser.add_argument('-m',
                        '--modelpath',
                        type=str,
                        default=os.path.join(
                            os.path.dirname(__file__),
                            'extensions'),
                        help='Path to model definition. ' +
                        'Can be a folder or a single file.')

    args = parser.parse_args()
    set_log_level_from_verbose(args)

    logger.info('Start parsing models')
    modelparser = Parser(args)
    # extend compiler with models
    modelparser.extend_compiler()

    # modelparser.remove_models()


def set_log_level_from_verbose(args):
    if not args.verbose:
        console_handler.setLevel('ERROR')
    elif args.verbose == 1:
        console_handler.setLevel('WARNING')
    elif args.verbose == 2:
        console_handler.setLevel('INFO')
    elif args.verbose >= 3:
        console_handler.setLevel('DEBUG')
    else:
        logger.critical("UNEXPLAINED NEGATIVE COUNT!")


if __name__ == '__main__':
    main()
