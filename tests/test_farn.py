import os
import platform
import re
from glob import glob
from pathlib import Path
from shutil import rmtree
import subprocess as sub

import pytest
from dictIO.dictReader import DictReader
from farn.farn import run_farn


farn_dirs = ['cases', 'cases-1layer', 'cases-2layer', 'cases-nofiltering', 'cases-initialfiltering', 'cases-excludefiltering', 'dump', 'logs', 'results', 'templates']
farn_files = ['queueList*', '*.copy', 'splash.png', 'caseList*']


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

    with open (infile, 'w') as f:
        f.write (re.sub(re.escape(query), substitution, buffer))


@pytest.mark.skip(reason='helper function')
def Split(cmd):
    cmd = re.sub(r'(^\'|\'$)', '', cmd)
    return re.split(r'\s+', cmd.strip())


@pytest.mark.skip(reason='helper function')
def is_string_in_stdout(stdout, string):
    try:
        assert re.findall(string, stdout.decode('utf-8'))[0]
        return True
    except:
        return False


@pytest.mark.skip(reason='farn opts have altered, no writing to file')
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


def test_console_verbosity():
    # test verbosity of console output

    # 10 samples, default verbosity
    command = '..\\src\\farn\\cli\\farn.py -s farnDict-nofiltering'
    S = sub.Popen(Split(command), stdout=sub.PIPE, stderr=sub.PIPE, shell=True)
    stdout, stderr = S.communicate()

    # must read
    assert is_string_in_stdout(stdout, 'Successfully listed 10 valid cases. 0 invalid case was excluded.')

    # 10 samples, default verbosity
    command = '..\\src\\farn\\cli\\farn.py -g sampled.farnDict-nofiltering'
    S = sub.Popen(Split(command), stdout=sub.PIPE, stderr=sub.PIPE, shell=True)
    stdout, stderr = S.communicate()

    # must read
    assert is_string_in_stdout(stdout, 'Successfully dropped 10 paramDict files in 10 case folders.')

    # must not read
    assert not is_string_in_stdout(stdout, 'creating case folder')

    # 10 samples, higher verbosity
    command = '..\\src\\farn\\cli\\farn.py -g sampled.farnDict-nofiltering -v'
    S = sub.Popen(Split(command), stdout=sub.PIPE, stderr=sub.PIPE, shell=True)
    stdout, stderr = S.communicate()
    # must read
    assert is_string_in_stdout(stdout, 'Successfully dropped 10 paramDict files in 10 case folders.')
    # must read
    assert is_string_in_stdout(stdout, 'creating case folder')


def test_filtering_output():
    # test some issues with filtering

    # filtering is applied before filter expression variables have been defined
    command = '..\\src\\farn\\cli\\farn.py -s farnDict-initialfiltering'
    S = sub.Popen(Split(command), stdout=sub.PIPE, stderr=sub.PIPE, shell=True)
    stdout, stderr = S.communicate()

    assert is_string_in_stdout(stdout, 'evaluation of the filter expression failed')

    # exception list filtering
    command = '..\\src\\farn\\cli\\farn.py -s farnDict-exceptionlistfiltering -v'
    S = sub.Popen(Split(command), stdout=sub.PIPE, stderr=sub.PIPE, shell=True)
    stdout, stderr = S.communicate()

    # condition layer 0 excludes everything with index not 1: here 0 an 2
    assert is_string_in_stdout(stdout, re.escape("The filter expression 'index != 1' evaluated to True."))
    # condition laxer 1 excludes everything where abs(param0*param1) >= 3.5: around 1 or 2 cases will survive depending on random variables
    assert is_string_in_stdout(stdout, re.escape("The filter expression 'abs(param0 * param1) >= 3.5' evaluated to True."))
    #assert is_string_in_stdout(stdout, "Action 'exclude' performed. Case lhsVariation_\d excluded.")


# testing subfiltering, 1 layer
def test_sample_1layer():
    # sample
    command = '..\\src\\farn\\cli\\farn.py -s test_farnDict_1layer'
    S = sub.Popen(Split(command), stdout=sub.PIPE, stderr=sub.PIPE, shell=True)
    stdout, stderr = S.communicate()

    # file
    assert os.path.exists('sampled.test_farnDict_1layer')

    # stdout
    assert is_string_in_stdout(stdout, re.escape('Successfully listed 2 valid cases. 1 invalid case was excluded.'))

    # generate
    command = '..\\src\\farn\\cli\\farn.py -g sampled.test_farnDict_1layer'
    S = sub.Popen(Split(command), stdout=sub.PIPE, stderr=sub.PIPE, shell=True)
    stdout, stderr = S.communicate()

    # folder
    assert os.path.exists('cases-1layer')

    # stdout
    assert is_string_in_stdout(stdout, re.escape('Successfully dropped 2 paramDict files in 2 case folders.'))

    # alter query string to locals() case name
    alter_farn_dict('sampled.test_farnDict_1layer', query='param0 > 2', substitution='name in ["layer0_1"]')

    # remove for later filtering being effective
    rmtree('cases-1layer', ignore_errors=True)

    # re-generate
    command = '..\\src\\farn\\cli\\farn.py -g sampled.test_farnDict_1layer'
    S = sub.Popen(Split(command), stdout=sub.PIPE, stderr=sub.PIPE, shell=True)
    stdout, stderr = S.communicate()

    # folder "layer0_1" must not exist
    assert not os.path.exists('cases-1layer\\layer0_1')

    # stdout shall contain
    assert is_string_in_stdout(stdout, 'Successfully listed 2 valid cases. 1 invalid case was excluded.')
    assert is_string_in_stdout(stdout, 'Successfully generated 2 case folders.')
    assert is_string_in_stdout(stdout, 'Successfully dropped 2 paramDict files in 2 case folders.')


# testing subfiltering, 2 layers
def test_sample_2layer():
    # sample
    command = '..\\src\\farn\\cli\\farn.py -s test_farnDict_2layer'
    S = sub.Popen(Split(command), stdout=sub.PIPE, stderr=sub.PIPE, shell=True)
    stdout, stderr = S.communicate()

    # file
    assert os.path.exists('sampled.test_farnDict_2layer')

    # stdout
    assert is_string_in_stdout(stdout, re.escape('Successfully listed 3 valid cases. 6 invalid cases were excluded.'))

    # generate
    command = '..\\src\\farn\\cli\\farn.py -g sampled.test_farnDict_2layer'
    S = sub.Popen(Split(command), stdout=sub.PIPE, stderr=sub.PIPE, shell=True)
    stdout, stderr = S.communicate()

    # folder
    assert os.path.exists('cases-2layer')

    # stdout
    assert is_string_in_stdout(stdout, re.escape('Successfully dropped 3 paramDict files in 3 case folders.'))

    # alter query string to locals() case name
    alter_farn_dict('sampled.test_farnDict_2layer', query='param1 > 2', substitution='name in ["layer2_0", "layer2_1"]')

    # remove for later filtering being effective
    rmtree('cases-2layer', ignore_errors=True)

    # re-generate
    command = '..\\src\\farn\\cli\\farn.py -g sampled.test_farnDict_2layer'
    S = sub.Popen(Split(command), stdout=sub.PIPE, stderr=sub.PIPE, shell=True)
    stdout, stderr = S.communicate()

    # folder
    assert not os.path.exists('cases-2layer\\layer1_0\\layers_0')

    # stdout shall contain
    assert is_string_in_stdout(stdout, 'Successfully listed 3 valid cases. 6 invalid cases were excluded.')
    assert is_string_in_stdout(stdout, 'Successfully generated 6 case folders.')
    assert is_string_in_stdout(stdout, 'Successfully dropped 3 paramDict files in 3 case folders.')
