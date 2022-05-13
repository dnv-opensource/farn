import os
from glob import glob
from pathlib import Path
from shutil import rmtree

import pytest


@pytest.fixture(scope='package', autouse=True)
def chdir():
    os.chdir(Path(__file__).parent.absolute() / 'test_dicts')


farn_dirs = [
    'cases',
    'cases_one_layer',
    'cases_two_layers',
    'cases_no_filtering',
    'cases_initial_filtering',
    'cases_exclude_filtering',
    'dump',
    'logs',
    'results',
    'templates',
]
farn_files = [
    'sampled*',
    'queueList*',
    '*.copy',
    'splash.png',
    'caseList*',
]


@pytest.fixture(autouse=True)
def default_setup_and_teardown():
    _remove_farn_dirs_and_files()
    yield
    _remove_farn_dirs_and_files()


def _remove_farn_dirs_and_files():
    for folder in farn_dirs:
        rmtree(folder, ignore_errors=True)
    for pattern in farn_files:
        for file in glob(pattern):
            file = Path(file)
            file.unlink(missing_ok=True)
