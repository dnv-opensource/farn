#!/usr/bin/env python
"""batchProcess command line interface."""

import argparse
import logging
import pprint
from importlib import metadata
from pathlib import Path

from farn.batch.batch_processor import AsyncBatchProcessor
from farn.utils.logging import configure_logging

logger = logging.getLogger(__name__)


def _get_version() -> str:
    """Return the installed package version, or a safe fallback if unavailable."""
    try:
        return metadata.version("farn")
    except metadata.PackageNotFoundError:
        # Fallback when package metadata is not available (e.g. running from source)
        return "farn (version unknown)"


def _argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="batchProcess",
        usage="%(prog)s caseList [options [args]]",
        epilog="_________________batchProcess___________________",
        prefix_chars="-",
        add_help=True,
        description=("Batch processes a list of cases, executing the specified shell command in all case folders."),
    )

    _ = parser.add_argument(
        "case_list_file",
        metavar="case_list_file",
        type=str,
        help="name of the text file containing all paths of the cases to be processed.",
    )

    _ = parser.add_argument(
        "-e",
        "--execute",
        metavar="command",
        action="store",
        type=str,
        help=(
            "shell command to execute in all case folders surrounded by double quotes, e.g. \n"
            '"cosim.exe run OspSystemStructure.xml -b 0 -d 20 --real-time -v"'
        ),
        default=None,
        required=True,
    )

    _ = parser.add_argument(
        "-t",
        "--timeout",
        action="store",
        type=int,
        help="timeout in seconds before an orphaned process gets killed",
        default=86400,
        required=False,
    )

    _ = parser.add_argument(
        "-c",
        "--cpu",
        action="store",
        type=int,
        help="max number of cpus to be used",
        default=0,
        required=False,
    )

    console_verbosity = parser.add_mutually_exclusive_group(required=False)

    _ = console_verbosity.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help=("console output will be quiet."),
        default=False,
    )

    _ = console_verbosity.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help=("console output will be verbose."),
        default=False,
    )

    _ = parser.add_argument(
        "--log",
        action="store",
        type=str,
        help="name of log file. If specified, this will activate logging to file.",
        default=None,
        required=False,
    )

    _ = parser.add_argument(
        "--log-level",
        action="store",
        type=str,
        help="log level applied to logging to file.",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="WARNING",
        required=False,
    )

    _ = parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=_get_version(),
    )

    return parser


def main() -> None:
    """Entry point for console script as configured in pyproject.toml.

    Runs the command line interface and parses arguments and options entered on the console.
    """
    parser = _argparser()
    args = parser.parse_args()

    # Configure Logging
    # ..to console
    log_level_console: str = "WARNING"
    if any([args.quiet, args.verbose]):
        log_level_console = "ERROR" if args.quiet else log_level_console
        log_level_console = "DEBUG" if args.verbose else log_level_console
    # ..to file
    log_file: Path | None = Path(args.log) if args.log else None
    log_level_file: str = args.log_level
    configure_logging(log_level_console, log_file, log_level_file)

    case_list_file: Path = Path(args.case_list_file)
    command: str = args.execute
    timeout: int = args.timeout
    max_number_of_cpus: int = args.cpu

    # Check whether case list file exists
    if not case_list_file.is_file():
        logger.error(f"batchProcess.py: File {case_list_file} not found.")
        return

    # Print the parsed commandline arguments for documentation and debugging purposes.
    # The arguments will be split into one argument per line, if possible.
    # If extracting a mapping from `args` fails, fall back to its string representation.
    _indent: str = " " * 13
    try:
        _arg_mapping = vars(args)
    except TypeError:
        _arg_mapping = {"args": str(args)}
    _formatted_args = pprint.pformat(_arg_mapping, sort_dicts=True)
    _indented_args = "\n".join(f"{_indent}{line}" for line in _formatted_args.splitlines())
    logger.info(
        "Start batchProcess.py with following arguments:\n%s\n",
        _indented_args,
    )

    # Invoke API
    batch_processor: AsyncBatchProcessor = AsyncBatchProcessor(
        case_list_file=case_list_file,
        command=command,
        timeout=timeout,
        max_number_of_cpus=max_number_of_cpus,
    )
    batch_processor.run()


if __name__ == "__main__":
    main()
