import os
import platform
import re
from glob import glob
from pathlib import Path
from shutil import rmtree

import pytest
from dictIO.dictReader import DictReader
from farn.farn import run_farn


farn_dirs = ['cases', 'cases-2layer', 'dump', 'logs', 'results', 'templates']
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

def alter_farn_dict(infile, query='', substitution=''):
    buffer = ''
    with open (infile, 'r') as f:
        buffer = f.read()

    print ('XXX',re.findall(query, buffer))
    with open (infile, 'w') as f:
        f.write (re.sub(query, substitution, buffer))

'''
def test_default_options():
    # farn opts have altered, no writing to file
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
        sample=False,
        generate=True,
        command=None,
        ignore_errors=False,
        test=False,
    )
    os.system('..\\src\\farn\\cli\\farn.py -s test_farnDict')
    farn_opts_read_from_farn_dict = DictReader.read(
        Path('sampled.test_farnDict'), scope=['_farnOpts']
    ).data
    assert farn_opts_read_from_farn_dict == farn_opts
'''

def test_sample():

    os.system('..\\src\\farn\\cli\\farn.py -s test_farnDict')

def test_generate():

    os.system('..\\src\\farn\\cli\\farn.py -g sampled.test_farnDict')


def test_regenerate():

    os.system('..\\src\\farn\\cli\\farn.py -g sampled.test_farnDict')
    os.system('..\\src\\farn\\cli\\farn.py -g sampled.test_farnDict')


def test_execute():
    os.system('..\\src\\farn\\cli\\farn.py -g sampled.test_farnDict')
    if platform.system() == 'Linux':
        os.system('farn.py sampled.test_farnDict -e testlinvar')
        os.system('farn.py sampled.test_farnDict -e printlinenv')
    else:
        os.system('..\\src\\farn\\cli\\farn.py sampled.test_farnDict -e testwinvar')
        os.system('..\\src\\farn\\cli\\farn.py sampled.test_farnDict -e printwinenv')



# testing subfiltering branch

def test_sample_2layer():
    os.system('..\\src\\farn\\cli\\farn.py -s test_farnDict_2layer')

def test_generate_2layer():
    os.system('..\\src\\farn\\cli\\farn.py -g sampled.test_farnDict_2layer')

def test_execute_2layer():
    # to test: normal filtering of variables from subdicts _names and _values
    os.system('..\\src\\farn\\cli\\farn.py -e sampled.test_farnDict_2layer')

# alter query string to locals() index
alter_farn_dict('sampled.test_farnDict_2layer', query='param1', substitution='index <= 23')

def test_execute_2layer():
    # to test if index is available
    os.system('..\\src\\farn\\cli\\farn.py -e sampled.test_farnDict_2layer')

# alter query string to locals() case_name
alter_farn_dict('sampled.test_farnDict_2layer', query='index <= 23', substitution="case_name in ['layer2_04', 'layer2_06', 'layer2_08']")

def test_execute_2layer():
    # to test if query in list
    os.system('..\\src\\farn\\cli\\farn.py -e sampled.test_farnDict_2layer')

# todo:
# re.sub failed to alter sampled.test_farnDict_2layer'
# test subsequent filtering activates formerly not generated case















