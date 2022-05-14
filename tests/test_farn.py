import os
import platform
from pathlib import Path

from farn.farn import run_farn


def test_sample():
    # Prepare
    farn_dict_file = Path('test_farnDict')
    sampled_file = Path(f'sampled.{farn_dict_file.name}')
    assert not sampled_file.exists()
    # Execute
    run_farn(farn_dict_file, sample=True)
    # Assert
    assert sampled_file.exists()


def test_generate(caplog):
    # Prepare
    farn_dict_file = Path('test_farnDict')
    sampled_file = Path(f'sampled.{farn_dict_file.name}')
    run_farn(farn_dict_file, sample=True)
    caplog.clear()
    # Execute
    run_farn(sampled_file, generate=True)
    # Assert
    assert Path('cases').exists()
    assert Path('cases/layer1_0').exists()
    assert Path('cases/layer1_1').exists()
    assert Path('cases/layer1_2').exists()


def test_regenerate(caplog):
    # Prepare
    farn_dict_file = Path('test_farnDict')
    sampled_file = Path(f'sampled.{farn_dict_file.name}')
    run_farn(farn_dict_file, sample=True)
    caplog.clear()
    # Execute
    run_farn(sampled_file, generate=True)
    run_farn(sampled_file, generate=True)
    # Assert
    assert Path('cases').exists()
    assert Path('cases/layer1_0').exists()
    assert Path('cases/layer1_1').exists()
    assert Path('cases/layer1_2').exists()


# @TODO: There is nothing  actually asserted in this test. -> Frank to check.
# CLAROS, 2022-05-13
def test_execute(caplog):
    # Prepare
    farn_dict_file = Path('test_farnDict')
    sampled_file = Path(f'sampled.{farn_dict_file.name}')
    run_farn(farn_dict_file, sample=True)
    run_farn(sampled_file, generate=True)
    caplog.clear()
    # Execute
    if platform.system() == 'Linux':
        os.system('farn.py sampled.test_farnDict -e testlinvar')
        os.system('farn.py sampled.test_farnDict -e printlinenv')
    else:
        os.system(f'python -m farn.cli.farn {sampled_file.name} --execute testwinvar')
        os.system(f'python -m farn.cli.farn {sampled_file.name} --execute printwinenv')
    # Assert


def test_sample_logging_verbosity_default(caplog):
    # Prepare
    farn_dict_file = Path('test_farnDict_no_filtering')
    # Execute
    run_farn(farn_dict_file, sample=True)
    out: str = caplog.text.rstrip()
    # Assert
    assert 'Successfully listed 10 valid cases. 0 invalid case was excluded.' in out


def test_generate_logging_verbosity_default(caplog):
    # Prepare
    farn_dict_file = Path('test_farnDict_no_filtering')
    sampled_file = Path(f'sampled.{farn_dict_file.name}')
    run_farn(farn_dict_file, sample=True)
    caplog.clear()
    # Execute
    run_farn(sampled_file, generate=True)
    out: str = caplog.text.rstrip()
    # Assert
    assert 'Successfully created 10 paramDict files in 10 case folders.' in out
    assert 'creating case folder' not in out


def test_sample_failed_filtering(caplog):
    # Prepare
    farn_dict_file = Path('test_farnDict_failed_filtering')
    sampled_file = Path(f'sampled.{farn_dict_file.name}')
    # Execute
    run_farn(farn_dict_file, sample=True)
    out: str = caplog.text.rstrip()
    # Assert
    # sampled dict should still have been written, although filtering could not successfully be executed
    assert sampled_file.exists()
    assert 'evaluation of the filter expression failed' in out


def test_sample_exclude_filtering(caplog):
    # Prepare
    farn_dict_file = Path('test_farnDict_exclude_filtering')
    caplog.set_level('DEBUG')
    # Execute
    run_farn(farn_dict_file, sample=True)
    out: str = caplog.text.rstrip()
    # Assert
    assert "The filter expression 'index != 1' evaluated to True." in out
    assert "The filter expression 'abs(param0 * param1) >= 3.5' evaluated to True." in out
    assert "Action 'exclude' performed. Case lhsVariation_" in out


def test_sample_filtering_one_layer_filter_layer(caplog):
    # Prepare
    farn_dict_file = Path('test_farnDict_one_layer_filter_layer')
    # Execute
    run_farn(farn_dict_file, sample=True)
    out: str = caplog.text.rstrip()
    # Assert
    assert 'Successfully listed 2 valid cases. 1 invalid case was excluded.' in out


def test_generate_filtering_one_layer_filter_layer(caplog):
    # Prepare
    farn_dict_file = Path('test_farnDict_one_layer_filter_layer')
    sampled_file = Path(f'sampled.{farn_dict_file.name}')
    run_farn(farn_dict_file, sample=True)
    caplog.clear()
    # Execute
    run_farn(sampled_file, generate=True)
    out: str = caplog.text.rstrip()
    # Assert
    # case folder 'layer0_1' must not exist
    assert not Path('cases_one_layer/layer0_1').exists()
    assert 'Successfully listed 2 valid cases. 1 invalid case was excluded.' in out
    assert 'Successfully created 2 case folders.' in out
    assert 'Successfully created 2 paramDict files in 2 case folders.' in out


def test_sample_filtering_one_layer_filter_param(caplog):
    # Prepare
    farn_dict_file = Path('test_farnDict_one_layer_filter_param')
    # Execute
    run_farn(farn_dict_file, sample=True)
    out: str = caplog.text.rstrip()
    # Assert
    assert 'Successfully listed 2 valid cases. 1 invalid case was excluded.' in out


def test_generate_filtering_one_layer_filter_param(caplog):
    # Prepare
    farn_dict_file = Path('test_farnDict_one_layer_filter_param')
    sampled_file = Path(f'sampled.{farn_dict_file.name}')
    run_farn(farn_dict_file, sample=True)
    caplog.clear()
    # Execute
    run_farn(sampled_file, generate=True)
    out: str = caplog.text.rstrip()
    # Assert
    assert Path('cases_one_layer').exists()
    assert 'Successfully created 2 paramDict files in 2 case folders.' in out


def test_sample_filtering_two_layers_filter_layer(caplog):
    # Prepare
    farn_dict_file = Path('test_farnDict_two_layers_filter_layer')
    # Execute
    run_farn(farn_dict_file, sample=True)
    out: str = caplog.text.rstrip()
    # Assert
    assert 'Successfully listed 3 valid cases. 6 invalid cases were excluded.' in out


def test_generate_filtering_two_layers_filter_layer(caplog):
    # Prepare
    farn_dict_file = Path('test_farnDict_two_layers_filter_layer')
    sampled_file = Path(f'sampled.{farn_dict_file.name}')
    run_farn(farn_dict_file, sample=True)
    caplog.clear()
    # Execute
    run_farn(sampled_file, generate=True)
    out: str = caplog.text.rstrip()
    # Assert
    # case folder 'layer1_0/layers_0' must not exist
    assert not Path('cases_two_layers/layer1_0/layers_0').exists()
    assert 'Successfully listed 3 valid cases. 6 invalid cases were excluded.' in out
    assert 'Successfully created 6 case folders.' in out
    assert 'Successfully created 3 paramDict files in 3 case folders.' in out


def test_sample_filtering_two_layers_filter_param(caplog):
    # Prepare
    farn_dict_file = Path('test_farnDict_two_layers_filter_param')
    # Execute
    run_farn(farn_dict_file, sample=True)
    out: str = caplog.text.rstrip()
    # Assert
    assert 'Successfully listed 3 valid cases. 6 invalid cases were excluded.' in out


def test_generate_filtering_two_layers_filter_param(caplog):
    # Prepare
    farn_dict_file = Path('test_farnDict_two_layers_filter_param')
    sampled_file = Path(f'sampled.{farn_dict_file.name}')
    run_farn(farn_dict_file, sample=True)
    caplog.clear()
    # Execute
    run_farn(sampled_file, generate=True)
    out: str = caplog.text.rstrip()
    # Assert
    assert Path('cases_two_layers').exists()
    assert 'Successfully created 3 paramDict files in 3 case folders.' in out
