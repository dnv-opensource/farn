# pyright: reportPrivateUsage=false
import sys
from argparse import ArgumentError
from dataclasses import dataclass
from pathlib import Path
from typing import List, Union

import pytest
from pytest import MonkeyPatch

from farn.cli import farn
from farn.cli.farn import _argparser, main

# *****Test commandline interface (CLI)************************************************************


@dataclass()
class CliArgs:
    # Expected default values for the CLI arguments when farn gets called via the commandline
    quiet: bool = False
    verbose: bool = False
    log: Union[str, None] = None
    log_level: str = "WARNING"
    farnDict: Union[str, None] = "test_farnDict"  # noqa
    sample: bool = False
    generate: bool = False
    execute: Union[str, None] = None
    test: bool = False


@pytest.mark.parametrize(
    "inputs, expected",
    [
        ([], ArgumentError),
        (["test_farnDict"], CliArgs()),
        (["test_farnDict", "-q"], CliArgs(quiet=True)),
        (["test_farnDict", "--quiet"], CliArgs(quiet=True)),
        (["test_farnDict", "-v"], CliArgs(verbose=True)),
        (["test_farnDict", "--verbose"], CliArgs(verbose=True)),
        (["test_farnDict", "-qv"], ArgumentError),
        (["test_farnDict", "--log", "logFile"], CliArgs(log="logFile")),
        (["test_farnDict", "--log"], ArgumentError),
        (["test_farnDict", "--log-level", "INFO"], CliArgs(log_level="INFO")),
        (["test_farnDict", "--log-level"], ArgumentError),
        (["test_farnDict", "-s"], CliArgs(sample=True)),
        (["test_farnDict", "--sample"], CliArgs(sample=True)),
        (["test_farnDict", "-g"], CliArgs(generate=True)),
        (["test_farnDict", "--generate"], CliArgs(generate=True)),
        (["test_farnDict", "-e", "command"], CliArgs(execute="command")),
        (["test_farnDict", "--execute", "command"], CliArgs(execute="command")),
        (
            ["test_farnDict", "--execute", "command name with spaces"],
            CliArgs(execute="command name with spaces"),
        ),
        (["test_farnDict", "--execute"], ArgumentError),
        (["test_farnDict", "--test"], CliArgs(test=True)),
        (["test_farnDict", "-t"], ArgumentError),
    ],
)
def test_cli(
    inputs: List[str],
    expected: Union[CliArgs, type],
    monkeypatch: MonkeyPatch,
):
    # Prepare
    monkeypatch.setattr(sys, "argv", ["farn"] + inputs)
    parser = _argparser()
    # Execute
    if isinstance(expected, CliArgs):
        args_expected: CliArgs = expected
        args = parser.parse_args()
        # Assert args
        for key in args_expected.__dataclass_fields__:
            assert args.__getattribute__(key) == args_expected.__getattribute__(key)
    elif issubclass(expected, Exception):
        exception: type = expected
        # Assert that expected exception is raised
        with pytest.raises((exception, SystemExit)):
            args = parser.parse_args()
    else:
        raise AssertionError()


# *****Ensure the CLI correctly configures logging*************************************************


@dataclass()
class ConfigureLoggingArgs:
    # Values that main() is expected to pass to ConfigureLogging() by default when configuring the logging
    log_level_console: str = "INFO"  # this deviates from standard 'WARNING', but was decided intentionally for farn
    log_file: Union[Path, None] = None
    log_level_file: str = "WARNING"


@pytest.mark.parametrize(
    "inputs, expected",
    [
        ([], ArgumentError),
        (["test_farnDict"], ConfigureLoggingArgs()),
        (["test_farnDict", "-q"], ConfigureLoggingArgs(log_level_console="ERROR")),
        (["test_farnDict", "--quiet"], ConfigureLoggingArgs(log_level_console="ERROR")),
        (["test_farnDict", "-v"], ConfigureLoggingArgs(log_level_console="DEBUG")),
        (
            ["test_farnDict", "--verbose"],
            ConfigureLoggingArgs(log_level_console="DEBUG"),
        ),
        (["test_farnDict", "-qv"], ArgumentError),
        (
            ["test_farnDict", "--log", "logFile"],
            ConfigureLoggingArgs(log_file=Path("logFile")),
        ),
        (["test_farnDict", "--log"], ArgumentError),
        (
            ["test_farnDict", "--log-level", "INFO"],
            ConfigureLoggingArgs(log_level_file="INFO"),
        ),
        (["test_farnDict", "--log-level"], ArgumentError),
    ],
)
def test_logging_configuration(
    inputs: List[str],
    expected: Union[ConfigureLoggingArgs, type],
    monkeypatch: MonkeyPatch,
):
    # Prepare
    monkeypatch.setattr(sys, "argv", ["farn"] + inputs)
    args: ConfigureLoggingArgs = ConfigureLoggingArgs()

    def fake_configure_logging(
        log_level_console: str,
        log_file: Union[Path, None],
        log_level_file: str,
    ):
        args.log_level_console = log_level_console
        args.log_file = log_file
        args.log_level_file = log_level_file

    def fake_run_farn(
        farn_dict_file: Path,
        sample: bool,
        generate: bool,
        command: Union[str, None],
        batch: bool,
        test: bool,
    ):
        pass

    monkeypatch.setattr(farn, "configure_logging", fake_configure_logging)
    monkeypatch.setattr(farn, "run_farn", fake_run_farn)
    # Execute
    if isinstance(expected, ConfigureLoggingArgs):
        args_expected: ConfigureLoggingArgs = expected
        main()
        # Assert args
        for key in args_expected.__dataclass_fields__:
            assert args.__getattribute__(key) == args_expected.__getattribute__(key)
    elif issubclass(expected, Exception):
        exception: type = expected
        # Assert that expected exception is raised
        with pytest.raises((exception, SystemExit)):
            main()
    else:
        raise AssertionError()


# *****Ensure the CLI correctly invokes the API****************************************************


@dataclass()
class ApiArgs:
    # Values that main() is expected to pass to run_farn() by default when invoking the API
    farn_dict_file: Path = Path("test_farnDict")
    sample: bool = False
    generate: bool = False
    command: Union[str, None] = None
    batch: bool = False
    test: bool = False


@pytest.mark.parametrize(
    "inputs, expected",
    [
        ([], ArgumentError),
        (["test_farnDict"], ApiArgs()),
        (["test_farnDict", "-s"], ApiArgs(sample=True)),
        (["test_farnDict", "--sample"], ApiArgs(sample=True)),
        (["test_farnDict", "-g"], ApiArgs(generate=True)),
        (["test_farnDict", "--generate"], ApiArgs(generate=True)),
        (["test_farnDict", "-e", "command"], ApiArgs(command="command")),
        (["test_farnDict", "--execute", "command"], ApiArgs(command="command")),
        (
            ["test_farnDict", "--execute", "command name with spaces"],
            ApiArgs(command="command name with spaces"),
        ),
        (["test_farnDict", "--execute"], ArgumentError),
        (["test_farnDict", "-b"], ApiArgs(batch=True)),
        (["test_farnDict", "--batch"], ApiArgs(batch=True)),
        (["test_farnDict", "--test"], ApiArgs(test=True)),
        (["test_farnDict", "-t"], ArgumentError),
    ],
)
def test_api_invokation(
    inputs: List[str],
    expected: Union[ApiArgs, type],
    monkeypatch: MonkeyPatch,
):
    # Prepare
    monkeypatch.setattr(sys, "argv", ["farn"] + inputs)
    args: ApiArgs = ApiArgs()

    def fake_run_farn(
        farn_dict_file: Path,
        sample: bool = False,
        generate: bool = False,
        command: Union[str, None] = None,
        batch: bool = False,
        test: bool = False,
    ):
        args.farn_dict_file = farn_dict_file
        args.sample = sample
        args.generate = generate
        args.command = command
        args.batch = batch
        args.test = test

    monkeypatch.setattr(farn, "run_farn", fake_run_farn)
    # Execute
    if isinstance(expected, ApiArgs):
        args_expected: ApiArgs = expected
        main()
        # Assert args
        for key in args_expected.__dataclass_fields__:
            assert args.__getattribute__(key) == args_expected.__getattribute__(key)
    elif issubclass(expected, Exception):
        exception: type = expected
        # Assert that expected exception is raised
        with pytest.raises((exception, SystemExit)):
            main()
    else:
        raise AssertionError()
