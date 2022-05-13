import os
import platform
import sys
from pathlib import Path


def test_sample():
    # Prepare
    farn_dict_file = Path('test_farnDict')
    sampled_file = Path(f'sampled.{farn_dict_file.name}')
    assert not sampled_file.exists()
    # Execute
    os.system(f'python -m farn.cli.farn --sample {farn_dict_file.name}')
    # Assert
    assert sampled_file.exists()


def test_generate():
    # Prepare
    farn_dict_file = Path('test_farnDict')
    sampled_file = Path(f'sampled.{farn_dict_file.name}')
    os.system(f'python -m farn.cli.farn --sample {farn_dict_file.name}')
    # Execute
    os.system(f'python -m farn.cli.farn --generate {sampled_file.name}')
    # Assert
    assert os.path.exists('cases')
    assert os.path.exists('cases/layer1_000')
    assert os.path.exists('cases/layer1_001')
    assert os.path.exists('cases/layer1_002')


def test_regenerate():
    # Prepare
    farn_dict_file = Path('test_farnDict')
    sampled_file = Path(f'sampled.{farn_dict_file.name}')
    os.system(f'python -m farn.cli.farn --sample {farn_dict_file.name}')
    # Execute
    os.system(f'python -m farn.cli.farn --generate {sampled_file.name}')
    os.system(f'python -m farn.cli.farn --generate {sampled_file.name}')
    # Assert
    assert os.path.exists('cases')
    assert os.path.exists('cases/layer1_000')
    assert os.path.exists('cases/layer1_001')
    assert os.path.exists('cases/layer1_002')


# @TODO: There is nothing  actually asserted in this test. -> Frank to check.
# CLAROS, 2022-05-13
def test_execute():
    # Prepare
    farn_dict_file = Path('test_farnDict')
    sampled_file = Path(f'sampled.{farn_dict_file.name}')
    os.system(f'python -m farn.cli.farn --sample {farn_dict_file.name}')
    os.system(f'python -m farn.cli.farn --generate {sampled_file.name}')
    # Execute
    if platform.system() == 'Linux':
        os.system('farn.py sampled.test_farnDict -e testlinvar')
        os.system('farn.py sampled.test_farnDict -e printlinenv')
    else:
        os.system(f'python -m farn.cli.farn {sampled_file.name} --execute testwinvar')
        os.system(f'python -m farn.cli.farn {sampled_file.name} --execute printwinenv')
    # Assert


def test_sample_logging_verbosity_default(monkeypatch, capsys):
    # Prepare
    from farn.cli.farn import main
    farn_dict_file = Path('test_farnDict_no_filtering')
    # Execute
    monkeypatch.setattr(sys, 'argv', ['farn', farn_dict_file.name, '-s'])
    main()
    out: str = capsys.readouterr().out.rstrip()
    # Assert
    assert 'Successfully listed 10 valid cases. 0 invalid case was excluded.' in out


def test_generate_logging_verbosity_default(monkeypatch, capsys):
    # Prepare
    from farn.cli.farn import main
    farn_dict_file = Path('test_farnDict_no_filtering')
    sampled_file = Path(f'sampled.{farn_dict_file.name}')
    os.system(f'python -m farn.cli.farn --sample {farn_dict_file.name}')
    # Execute
    monkeypatch.setattr(sys, 'argv', ['farn', sampled_file.name, '-g'])
    main()
    out: str = capsys.readouterr().out.rstrip()
    # Assert
    assert 'Successfully dropped 10 paramDict files in 10 case folders.' in out
    assert 'creating case folder' not in out


def test_generate_logging_verbosity_verbose(monkeypatch, capsys):
    # Prepare
    from farn.cli.farn import main
    farn_dict_file = Path('test_farnDict_no_filtering')
    sampled_file = Path(f'sampled.{farn_dict_file.name}')
    os.system(f'python -m farn.cli.farn --sample {farn_dict_file.name}')
    # Execute
    monkeypatch.setattr(sys, 'argv', ['farn', sampled_file.name, '-g', '-v'])
    main()
    out: str = capsys.readouterr().out.rstrip()
    # Assert
    assert 'Successfully dropped 10 paramDict files in 10 case folders.' in out
    assert 'creating case folder' in out


def test_sample_failed_filtering(monkeypatch, capsys):
    # Prepare
    from farn.cli.farn import main
    farn_dict_file = Path('test_farnDict_failed_filtering')
    sampled_file = Path(f'sampled.{farn_dict_file.name}')
    # Execute
    monkeypatch.setattr(sys, 'argv', ['farn', farn_dict_file.name, '-s'])
    main()
    out: str = capsys.readouterr().out.rstrip()
    # Assert
    # sampled dict should still have been written, although filtering could not successfully be executed
    assert sampled_file.exists()
    assert 'evaluation of the filter expression failed' in out


def test_sample_exclude_filtering(monkeypatch, capsys):
    # Prepare
    from farn.cli.farn import main
    farn_dict_file = Path('test_farnDict_exclude_filtering')
    # Execute
    monkeypatch.setattr(sys, 'argv', ['farn', farn_dict_file.name, '-s', '-v'])
    main()
    out: str = capsys.readouterr().out.rstrip()
    # Assert
    assert "The filter expression 'index != 1' evaluated to True." in out
    assert "The filter expression 'abs(param0 * param1) >= 3.5' evaluated to True." in out
    assert "Action 'exclude' performed. Case lhsVariation_" in out


def test_sample_filtering_one_layer_filter_layer(monkeypatch, capsys):
    # Prepare
    from farn.cli.farn import main
    farn_dict_file = Path('test_farnDict_one_layer_filter_layer')
    # Execute
    monkeypatch.setattr(sys, 'argv', ['farn', farn_dict_file.name, '-s'])
    main()
    out: str = capsys.readouterr().out.rstrip()
    # Assert
    assert 'Successfully listed 2 valid cases. 1 invalid case was excluded.' in out


def test_generate_filtering_one_layer_filter_layer(monkeypatch, capsys):
    # Prepare
    from farn.cli.farn import main
    farn_dict_file = Path('test_farnDict_one_layer_filter_layer')
    sampled_file = Path(f'sampled.{farn_dict_file.name}')
    os.system(f'python -m farn.cli.farn --sample {farn_dict_file.name}')
    # Execute
    monkeypatch.setattr(sys, 'argv', ['farn', sampled_file.name, '-g'])
    main()
    out: str = capsys.readouterr().out.rstrip()
    # Assert
    # case folder 'layer0_1' must not exist
    assert not os.path.exists('cases_one_layer/layer0_1')
    assert 'Successfully listed 2 valid cases. 1 invalid case was excluded.' in out
    assert 'Successfully generated 2 case folders.' in out
    assert 'Successfully dropped 2 paramDict files in 2 case folders.' in out


def test_sample_filtering_one_layer_filter_param(monkeypatch, capsys):
    # Prepare
    from farn.cli.farn import main
    farn_dict_file = Path('test_farnDict_one_layer_filter_param')
    # Execute
    monkeypatch.setattr(sys, 'argv', ['farn', farn_dict_file.name, '-s'])
    main()
    out: str = capsys.readouterr().out.rstrip()
    # Assert
    assert 'Successfully listed 2 valid cases. 1 invalid case was excluded.' in out


def test_generate_filtering_one_layer_filter_param(monkeypatch, capsys):
    # Prepare
    from farn.cli.farn import main
    farn_dict_file = Path('test_farnDict_one_layer_filter_param')
    sampled_file = Path(f'sampled.{farn_dict_file.name}')
    os.system(f'python -m farn.cli.farn --sample {farn_dict_file.name}')
    # Execute
    monkeypatch.setattr(sys, 'argv', ['farn', sampled_file.name, '-g'])
    main()
    out: str = capsys.readouterr().out.rstrip()
    # Assert
    assert os.path.exists('cases_one_layer')
    assert 'Successfully dropped 2 paramDict files in 2 case folders.' in out


def test_sample_filtering_two_layers_filter_layer(monkeypatch, capsys):
    # Prepare
    from farn.cli.farn import main
    farn_dict_file = Path('test_farnDict_two_layers_filter_layer')
    # Execute
    monkeypatch.setattr(sys, 'argv', ['farn', farn_dict_file.name, '-s'])
    main()
    out: str = capsys.readouterr().out.rstrip()
    # Assert
    assert 'Successfully listed 3 valid cases. 6 invalid cases were excluded.' in out


def test_generate_filtering_two_layers_filter_layer(monkeypatch, capsys):
    # Prepare
    from farn.cli.farn import main
    farn_dict_file = Path('test_farnDict_two_layers_filter_layer')
    sampled_file = Path(f'sampled.{farn_dict_file.name}')
    os.system(f'python -m farn.cli.farn --sample {farn_dict_file.name}')
    # Execute
    monkeypatch.setattr(sys, 'argv', ['farn', sampled_file.name, '-g'])
    main()
    out: str = capsys.readouterr().out.rstrip()
    # Assert
    # case folder 'layer1_0/layers_0' must not exist
    assert not os.path.exists('cases_two_layers/layer1_0/layers_0')
    assert 'Successfully listed 3 valid cases. 6 invalid cases were excluded.' in out
    assert 'Successfully generated 6 case folders.' in out
    assert 'Successfully dropped 3 paramDict files in 3 case folders.' in out


def test_sample_filtering_two_layers_filter_param(monkeypatch, capsys):
    # Prepare
    from farn.cli.farn import main
    farn_dict_file = Path('test_farnDict_two_layers_filter_param')
    # Execute
    monkeypatch.setattr(sys, 'argv', ['farn', farn_dict_file.name, '-s'])
    main()
    out: str = capsys.readouterr().out.rstrip()
    # Assert
    assert 'Successfully listed 3 valid cases. 6 invalid cases were excluded.' in out


def test_generate_filtering_two_layers_filter_param(monkeypatch, capsys):
    # Prepare
    from farn.cli.farn import main
    farn_dict_file = Path('test_farnDict_two_layers_filter_param')
    sampled_file = Path(f'sampled.{farn_dict_file.name}')
    os.system(f'python -m farn.cli.farn --sample {farn_dict_file.name}')
    # Execute
    monkeypatch.setattr(sys, 'argv', ['farn', sampled_file.name, '-g'])
    main()
    out: str = capsys.readouterr().out.rstrip()
    # Assert
    assert os.path.exists('cases_two_layers')
    assert 'Successfully dropped 3 paramDict files in 3 case folders.' in out
