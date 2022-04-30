import os
import platform
import re
from glob import glob
from pathlib import Path
from shutil import rmtree
import sys

import pytest
from dictIO.utils.path import silent_remove


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
    'templates'
]
farn_files = ['queueList*', '*.copy', 'splash.png', 'caseList*']


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


def test_logging_verbosity(monkeypatch, capsys):
    # test verbosity of logging
    from farn.cli.farn import main
    # Prepare
    farn_dict_file = Path('test_farnDict_no_filtering')
    sampled_file = Path('sampled.test_farnDict_no_filtering')
    silent_remove(sampled_file)

    # Execute --sample with default verbosity
    monkeypatch.setattr(sys, 'argv', ['farn', farn_dict_file.name, '-s'])
    main()
    out: str = capsys.readouterr().out.rstrip()
    # Assert
    assert sampled_file.exists()
    assert 'Successfully listed 10 valid cases. 0 invalid case was excluded.' in out

    # Execute --generate with default verbosity
    monkeypatch.setattr(sys, 'argv', ['farn', sampled_file.name, '-g'])
    main()
    out: str = capsys.readouterr().out.rstrip()
    # Assert
    assert 'Successfully dropped 10 paramDict files in 10 case folders.' in out
    assert 'creating case folder' not in out

    # Execute --generate with higher verbosity
    monkeypatch.setattr(sys, 'argv', ['farn', sampled_file.name, '-g', '-v'])
    main()
    out: str = capsys.readouterr().out.rstrip()
    # Assert
    assert 'Successfully dropped 10 paramDict files in 10 case folders.' in out
    assert 'creating case folder' in out

    # Clean up
    silent_remove(sampled_file)


def test_failed_filtering(monkeypatch, capsys):
    # test_farnDict_failed_filtering contains a common mistake:
    # A filter expression references a variable that has not (yet) been defined
    # Prepare
    from farn.cli.farn import main
    farn_dict_file = Path('test_farnDict_failed_filtering')
    sampled_file = Path('sampled.test_farnDict_failed_filtering')
    silent_remove(sampled_file)
    # Execute
    monkeypatch.setattr(sys, 'argv', ['farn', farn_dict_file.name, '-s'])
    main()
    out: str = capsys.readouterr().out.rstrip()
    # Assert
    assert sampled_file.exists()
    assert 'evaluation of the filter expression failed' in out
    # Clean up
    silent_remove(sampled_file)


def test_exclude_filtering(monkeypatch, capsys):
    # Prepare
    from farn.cli.farn import main
    farn_dict_file = Path('test_farnDict_exclude_filtering')
    sampled_file = Path('sampled.test_farnDict_exclude_filtering')
    silent_remove(sampled_file)
    # Execute
    monkeypatch.setattr(sys, 'argv', ['farn', farn_dict_file.name, '-s', '-v'])
    main()
    out: str = capsys.readouterr().out.rstrip()
    # Assert
    assert sampled_file.exists()
    # condition in layer 0 excludes everything with index not 1: here 0 an 2
    assert "The filter expression 'index != 1' evaluated to True." in out
    # condition in layer 1 excludes everything where abs(param0*param1) >= 3.5: around 1 or 2 cases will survive depending on random variables
    assert "The filter expression 'abs(param0 * param1) >= 3.5' evaluated to True." in out
    assert "Action 'exclude' performed. Case lhsVariation_" in out
    # Clean up
    silent_remove(sampled_file)


def test_filtering_one_layer(monkeypatch, capsys):
    # test filtering, one layer
    from farn.cli.farn import main
    # Prepare
    farn_dict_file = Path('test_farnDict_one_layer')
    sampled_file = Path('sampled.test_farnDict_one_layer')
    silent_remove(sampled_file)
    # Execute --sample
    monkeypatch.setattr(sys, 'argv', ['farn', farn_dict_file.name, '-s'])
    main()
    out: str = capsys.readouterr().out.rstrip()
    # Assert
    assert sampled_file.exists()
    assert 'Successfully listed 2 valid cases. 1 invalid case was excluded.' in out

    # Execute --generate
    monkeypatch.setattr(sys, 'argv', ['farn', sampled_file.name, '-g'])
    main()
    out: str = capsys.readouterr().out.rstrip()
    # Assert
    assert os.path.exists('cases_one_layer')
    assert 'Successfully dropped 2 paramDict files in 2 case folders.' in out

    # Alter query string to locals() case name
    _alter_farn_dict(sampled_file.name, query='param0 > 2', substitution='case in ["layer0_1"]')
    # Remove case folder in order for altered filtering during generation to be effective
    rmtree('cases_one_layer', ignore_errors=True)

    # re-generate
    monkeypatch.setattr(sys, 'argv', ['farn', sampled_file.name, '-g'])
    main()
    out: str = capsys.readouterr().out.rstrip()
    # Assert
    assert not os.path.exists('cases_one_layer/layer0_1')   # case folder 'layer0_1' must not exist
    assert 'Successfully listed 2 valid cases. 1 invalid case was excluded.' in out
    assert 'Successfully generated 2 case folders.' in out
    assert 'Successfully dropped 2 paramDict files in 2 case folders.' in out

    # Clean up
    silent_remove(sampled_file)
    rmtree('cases_one_layer', ignore_errors=True)
    rmtree('logs', ignore_errors=True)


def test_filtering_two_layers(monkeypatch, capsys):
    # test filtering, two layers
    from farn.cli.farn import main
    # Prepare
    farn_dict_file = Path('test_farnDict_two_layers')
    sampled_file = Path('sampled.test_farnDict_two_layers')
    silent_remove(sampled_file)
    # Execute --sample
    monkeypatch.setattr(sys, 'argv', ['farn', farn_dict_file.name, '-s'])
    main()
    out: str = capsys.readouterr().out.rstrip()
    # Assert
    assert sampled_file.exists()
    assert 'Successfully listed 3 valid cases. 6 invalid cases were excluded.' in out

    # Execute --generate
    monkeypatch.setattr(sys, 'argv', ['farn', sampled_file.name, '-g'])
    main()
    out: str = capsys.readouterr().out.rstrip()
    # Assert
    assert os.path.exists('cases_two_layers')
    assert 'Successfully dropped 3 paramDict files in 3 case folders.' in out

    # Alter query string to locals() case name
    _alter_farn_dict(
        sampled_file.name, query='param1 > 2', substitution='case in ["layer2_0", "layer2_1"]'
    )
    # Remove case folder in order for altered filtering during generation to be effective
    rmtree('cases_two_layers', ignore_errors=True)

    # re-generate
    monkeypatch.setattr(sys, 'argv', ['farn', sampled_file.name, '-g'])
    main()
    out: str = capsys.readouterr().out.rstrip()
    # Assert
    assert not os.path.exists(
        'cases_two_layers/layer1_0/layers_0'
    )                                           # case folder 'layer1_0/layers_0' must not exist
    assert 'Successfully listed 3 valid cases. 6 invalid cases were excluded.' in out
    assert 'Successfully generated 6 case folders.' in out
    assert 'Successfully dropped 3 paramDict files in 3 case folders.' in out

    # Clean up
    silent_remove(sampled_file)
    rmtree('cases_two_layers', ignore_errors=True)


def _alter_farn_dict(infile, query='', substitution=''):
    buffer = ''
    with open(infile, 'r') as f:
        buffer = f.read()

    with open(infile, 'w') as f:
        f.write(re.sub(re.escape(query), substitution, buffer))


def _split_command(cmd):
    cmd = re.sub(r'(^\'|\'$)', '', cmd)
    return re.split(r'\s+', cmd.strip())
