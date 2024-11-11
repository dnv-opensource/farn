import logging
import os
from pathlib import Path
from shutil import rmtree

import pytest


@pytest.fixture(scope="package", autouse=True)
def chdir() -> None:
    """
    Fixture that changes the current working directory to the 'test_working_directory' folder.
    This fixture is automatically used for the entire package.
    """
    os.chdir(Path(__file__).parent.absolute() / "test_dicts")


@pytest.fixture(scope="package", autouse=True)
def test_dir() -> Path:
    """
    Fixture that returns the absolute path of the directory containing the current file.
    This fixture is automatically used for the entire package.
    """
    return Path(__file__).parent.absolute()


output_dirs = [
    "cases",
    "cases_one_layer",
    "cases_two_layers",
    "cases_no_filtering",
    "cases_initial_filtering",
    "cases_exclude_filtering",
    "dump",
    "logs",
    "results",
    "templates",
]
output_files = [
    "sampled*",
    "queueList*",
    "*.copy",
    "splash.png",
    "caseList*",
]


@pytest.fixture(autouse=True)
def default_setup_and_teardown():
    """
    Fixture that performs setup and teardown actions before and after each test function.
    It removes the output directories and files specified in 'output_dirs' and 'output_files' lists.
    """
    _remove_output_dirs_and_files()
    yield
    _remove_output_dirs_and_files()


def _remove_output_dirs_and_files() -> None:
    """
    Helper function that removes the output directories and files specified in 'output_dirs' and 'output_files' lists.
    """
    for folder in output_dirs:
        rmtree(folder, ignore_errors=True)
    for pattern in output_files:
        for file in Path.cwd().glob(pattern):
            _file = Path(file)
            _file.unlink(missing_ok=True)


@pytest.fixture(autouse=True)
def setup_logging(caplog: pytest.LogCaptureFixture) -> None:
    """
    Fixture that sets up logging for each test function.
    It sets the log level to 'INFO' and clears the log capture.
    """
    caplog.set_level("INFO")
    caplog.clear()


@pytest.fixture(autouse=True)
def logger() -> logging.Logger:
    """Fixture that returns the logger object."""
    return logging.getLogger()
