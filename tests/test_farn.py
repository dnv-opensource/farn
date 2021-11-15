import os
import platform
from glob import glob
from pathlib import Path
from shutil import rmtree

import pytest
from dictIO.dictReader import DictReader
from farn.farn import run_farn


farn_dirs = ['cases', 'dump', 'logs', 'results', 'templates']
farn_files = ['queueList*', '*.copy', 'splash.png', 'caseList']


@pytest.fixture(autouse=True)
def default_setup_and_teardown():
    remove_farn_dirs_and_files()
    yield
    remove_farn_dirs_and_files()


def remove_farn_dirs_and_files():
    for folder in farn_dirs:
        rmtree(folder, ignore_errors=True)
    for pattern in farn_files:
        for file in glob(pattern):
            file = Path(file)
            file.unlink(missing_ok=True)


def test_default_options():
    farn_opts = {
        'farnDict': 'test_farnDict',
        'runSampling': False,
        'generate': True,
        'execute': None,
        'ignore-errors': False,
        'test': False,
    }
    run_farn(
        Path('test_farnDict'),
        run_sampling=False,
        generate=True,
        command=None,
        ignore_errors=False,
        test=False,
    )
    os.system('..\\src\\farn\\cli\\farn.py -g test_farnDict')
    farn_opts_read_from_farn_dict = DictReader.read(
        Path('test_farnDict.copy'), scope=['_farnOpts']
    ).data
    assert farn_opts_read_from_farn_dict == farn_opts


def test_generate():

    os.system('..\\src\\farn\\cli\\farn.py -g test_farnDict')


def test_regenerate():

    os.system('..\\src\\farn\\cli\\farn.py -g test_farnDict')
    os.system('..\\src\\farn\\cli\\farn.py -g test_farnDict')


def test_execute():
    os.system('..\\src\\farn\\cli\\farn.py -g test_farnDict')
    if platform.system() == 'Linux':
        os.system('farn.py test_farnDict -e testlinvar')
        os.system('farn.py test_farnDict -e printlinenv')
    else:
        os.system('..\\src\\farn\\cli\\farn.py test_farnDict -e testwinvar')
        os.system('..\\src\\farn\\cli\\farn.py test_farnDict -e printwinenv')
