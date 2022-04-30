#!/usr/bin/env python
# coding: utf-8

import argparse
import logging
from argparse import ArgumentParser
from pathlib import Path
from typing import Union

from farn.run.batchProcess import AsyncBatchProcessor
from farn.utils.logging import configure_logging


logger = logging.getLogger(__name__)


def _argparser() -> argparse.ArgumentParser:

    parser = ArgumentParser(
        prog='batchProcess',
        usage='%(prog)s caseList [options [args]]',
        epilog='_________________batchProcess___________________',
        prefix_chars='-',
        add_help=True,
        description=(
            'Batch processes a list of cases, executing the specified shell command in all case folders.'
        )
    )

    parser.add_argument(
        'caseList',
        metavar='caseList',
        type=str,
        help='name of the text file containing all paths of the cases to be processed.',
    )

    parser.add_argument(
        '-e',
        '--execute',
        metavar='CMD',
        action='store',
        type=str,
        help=(
            "shell command to execute in all case folders surrounded by double quotes, e.g. \n"
            '"cosim.exe run OspSystemStructure.xml -b 0 -d 20 --real-time -v"'
        ),
        default=None,
        required=True,
    )

    parser.add_argument(
        '-t',
        '--timeout',
        action='store',
        type=int,
        help='timeout in seconds before an orphaned process gets killed',
        default=86400,
        required=False,
    )

    parser.add_argument(
        '-c',
        '--cpu',
        action='store',
        type=int,
        help='max number of cpus to be used',
        default=0,
        required=False,
    )

    console_verbosity = parser.add_mutually_exclusive_group(required=False)

    console_verbosity.add_argument(
        '-q',
        '--quiet',
        action='store_true',
        help=('console output will be quiet.'),
        default=False,
    )

    console_verbosity.add_argument(
        '-v',
        '--verbose',
        action='store_true',
        help=('console output will be verbose.'),
        default=False,
    )

    parser.add_argument(
        '--log',
        action='store',
        type=str,
        help='name of log file. If specified, this will activate logging to file.',
        default=None,
        required=False,
    )

    parser.add_argument(
        '--log-level',
        action='store',
        type=str,
        help='log level applied to logging to file.',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='WARNING',
        required=False,
    )

    return parser


def main():
    """Entry point for console script as configured in setup.cfg

    Runs the command line interface and parses arguments and options entered on the console.
    """

    parser = _argparser()
    args = parser.parse_args()

    # Configure Logging
    # ..to console
    log_level_console: str = 'WARNING'
    if any([args.quiet, args.verbose]):
        log_level_console = 'ERROR' if args.quiet else log_level_console
        log_level_console = 'DEBUG' if args.verbose else log_level_console
    # ..to file
    log_file: Union[Path, None] = Path(args.log) if args.log else None
    log_level_file: str = args.log_level
    configure_logging(log_level_console, log_file, log_level_file)

    case_list_file: Path = Path(args.caseList)
    command: str = args.execute
    timeout: int = args.timeout
    max_number_of_cpus: int = args.cpu

    # Check whether caselist file exists
    if not case_list_file.is_file():
        logger.error(f'runCases.py: File {case_list_file} not found.')
        return

    # Invoke API
    batch_processor: AsyncBatchProcessor = AsyncBatchProcessor(
        case_list_file=case_list_file,
        command=command,
        timeout=timeout,
        max_number_of_cpus=max_number_of_cpus,
    )
    batch_processor.run()


if __name__ == '__main__':
    main()
