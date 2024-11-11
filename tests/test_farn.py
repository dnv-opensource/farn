import os
from pathlib import Path
from typing import Any

import pytest
from dictIO import DictReader, SDict

from farn import create_cases, create_samples, run_farn
from farn.core import Cases


def test_sample() -> None:
    # Prepare
    farn_dict_file = Path("test_farnDict_v4")
    sampled_file = Path(f"sampled.{farn_dict_file.name}")
    assert not sampled_file.exists()
    # Execute
    _ = run_farn(farn_dict_file, sample=True)
    # Assert
    assert sampled_file.exists()


def test_create_samples() -> None:
    # Prepare
    farn_dict_file = Path("test_farnDict_v4")
    farn_dict: SDict[str, Any] = DictReader.read(farn_dict_file, comments=False)
    sampled_file = Path(f"sampled.{farn_dict_file.name}")
    _ = run_farn(farn_dict_file, sample=True)
    sampled_farn_dict_assert: SDict[str, Any] = DictReader.read(sampled_file)
    # Execute
    create_samples(farn_dict)
    # Assert
    assert "_samples" in farn_dict["_layers"]["gp"]
    assert "_samples" in farn_dict["_layers"]["lhsvar"]
    assert "_samples" in farn_dict["_layers"]["cp"]
    assert "_samples" in farn_dict["_layers"]["hilbert"]
    assert "_samples" in farn_dict["_layers"]["mp"]
    assert len(farn_dict["_layers"]["gp"]) == len(sampled_farn_dict_assert["_layers"]["gp"])
    assert len(farn_dict["_layers"]["lhsvar"]) == len(sampled_farn_dict_assert["_layers"]["lhsvar"])
    assert len(farn_dict["_layers"]["cp"]) == len(sampled_farn_dict_assert["_layers"]["cp"])
    assert len(farn_dict["_layers"]["hilbert"]) == len(sampled_farn_dict_assert["_layers"]["hilbert"])
    assert len(farn_dict["_layers"]["mp"]) == len(sampled_farn_dict_assert["_layers"]["mp"])


def test_create_cases() -> None:
    # Prepare
    farn_dict_file = Path("test_farnDict_no_filtering")
    farn_dict: SDict[str, Any] = DictReader.read(farn_dict_file, comments=False)
    create_samples(farn_dict)
    case_dir: Path = Path.cwd()
    # Execute
    cases: Cases = create_cases(farn_dict, case_dir, valid_only=True)
    # Assert
    assert isinstance(cases, Cases)
    assert len(cases) == 12


def test_generate(caplog: pytest.LogCaptureFixture) -> None:
    # Prepare
    farn_dict_file = Path("test_farnDict")
    sampled_file = Path(f"sampled.{farn_dict_file.name}")
    _ = run_farn(farn_dict_file, sample=True)
    caplog.clear()
    # Execute
    _ = run_farn(sampled_file, generate=True)
    # Assert
    assert Path("cases").exists()
    assert Path("cases/layer1_0").exists()
    assert Path("cases/layer1_1").exists()
    assert Path("cases/layer1_2").exists()


def test_regenerate(caplog: pytest.LogCaptureFixture) -> None:
    # Prepare
    farn_dict_file = Path("test_farnDict")
    sampled_file = Path(f"sampled.{farn_dict_file.name}")
    _ = run_farn(farn_dict_file, sample=True)
    caplog.clear()
    # Execute
    _ = run_farn(sampled_file, generate=True)
    _ = run_farn(sampled_file, generate=True)
    # Assert
    assert Path("cases").exists()
    assert Path("cases/layer1_0").exists()
    assert Path("cases/layer1_1").exists()
    assert Path("cases/layer1_2").exists()


def test_always_distribute_parameters() -> None:
    # Prepare
    farn_dict_file = Path("test_farnDict_always_distribute")
    sampled_file = Path(f"sampled.{farn_dict_file.name}")
    _ = run_farn(farn_dict_file, sample=True)
    # Execute
    _ = run_farn(sampled_file, generate=True)
    # Assert
    assert Path("cases").exists()
    assert Path("cases/linspaceLayer_0").exists()
    assert Path("cases/linspaceLayer_0").exists()
    # test one output
    param_dict_file = Path("cases/linspaceLayer_0/paramDict")
    param_dict: SDict[str, Any] = DictReader.read(param_dict_file, comments=False)

    assert param_dict["param0"] == 0.0
    assert param_dict["param1"] == 1.0
    assert param_dict["param2"] == 2.0


# @TODO: There is nothing  actually asserted in this test. -> Frank to check.
# CLAROS, 2022-05-13
def test_execute(caplog: pytest.LogCaptureFixture) -> None:
    # sourcery skip: no-conditionals-in-tests
    # Prepare
    farn_dict_file = Path("test_farnDict")
    sampled_file = Path(f"sampled.{farn_dict_file.name}")
    _ = run_farn(farn_dict_file, sample=True)
    _ = run_farn(sampled_file, generate=True)
    caplog.clear()
    # Execute
    _ = os.system(f"farn {sampled_file.name} --execute testwinvar")  # noqa: S605
    _ = os.system(f"farn {sampled_file.name} --execute printwinenv")  # noqa: S605
    # Assert


def test_sample_logging_verbosity_default(caplog: pytest.LogCaptureFixture) -> None:
    # Prepare
    farn_dict_file = Path("test_farnDict_no_filtering")
    # Execute
    _ = run_farn(farn_dict_file, sample=True)
    out: str = caplog.text.rstrip()
    # Assert
    assert "Successfully listed 10 valid cases. 0 invalid case was excluded." in out


def test_generate_logging_verbosity_default(caplog: pytest.LogCaptureFixture) -> None:
    # Prepare
    farn_dict_file = Path("test_farnDict_no_filtering")
    sampled_file = Path(f"sampled.{farn_dict_file.name}")
    _ = run_farn(farn_dict_file, sample=True)
    caplog.clear()
    # Execute
    _ = run_farn(sampled_file, generate=True)
    out: str = caplog.text.rstrip()
    # Assert
    assert "Successfully created 10 paramDict files in 10 case folders." in out
    assert "creating case folder" not in out


def test_sample_failed_filtering(caplog: pytest.LogCaptureFixture) -> None:
    # Prepare
    farn_dict_file = Path("test_farnDict_failed_filtering")
    sampled_file = Path(f"sampled.{farn_dict_file.name}")
    # Execute
    _ = run_farn(farn_dict_file, sample=True)
    out: str = caplog.text.rstrip()
    # Assert
    # sampled dict should still have been written, although filtering could not successfully be executed
    assert sampled_file.exists()
    assert "evaluation of the filter expression failed" in out


def test_sample_exclude_filtering(caplog: pytest.LogCaptureFixture) -> None:
    # Prepare
    farn_dict_file = Path("test_farnDict_exclude_filtering")
    caplog.set_level("DEBUG")
    # Execute
    _ = run_farn(farn_dict_file, sample=True)
    out: str = caplog.text.rstrip()
    # Assert
    assert "The filter expression 'index != 1' evaluated to True." in out
    assert "The filter expression 'abs(param0 * param1) >= 3.5' evaluated to True." in out
    assert "Action 'exclude' performed. Case lhsVariation_" in out


def test_sample_filtering_one_layer_filter_layer(caplog: pytest.LogCaptureFixture) -> None:
    # Prepare
    farn_dict_file = Path("test_farnDict_one_layer_filter_layer")
    # Execute
    _ = run_farn(farn_dict_file, sample=True)
    out: str = caplog.text.rstrip()
    # Assert
    assert "Successfully listed 2 valid cases. 1 invalid case was excluded." in out


def test_generate_filtering_one_layer_filter_layer(caplog: pytest.LogCaptureFixture) -> None:
    # Prepare
    farn_dict_file = Path("test_farnDict_one_layer_filter_layer")
    sampled_file = Path(f"sampled.{farn_dict_file.name}")
    _ = run_farn(farn_dict_file, sample=True)
    caplog.clear()
    # Execute
    _ = run_farn(sampled_file, generate=True)
    out: str = caplog.text.rstrip()
    # Assert
    # case folder 'layer0_1' must not exist
    assert not Path("cases_one_layer/layer0_1").exists()
    assert "Successfully listed 2 valid cases. 1 invalid case was excluded." in out
    assert "Successfully created 2 case folders." in out
    assert "Successfully created 2 paramDict files in 2 case folders." in out


def test_sample_filtering_one_layer_filter_param(caplog: pytest.LogCaptureFixture) -> None:
    # Prepare
    farn_dict_file = Path("test_farnDict_one_layer_filter_param")
    # Execute
    _ = run_farn(farn_dict_file, sample=True)
    out: str = caplog.text.rstrip()
    # Assert
    assert "Successfully listed 2 valid cases. 1 invalid case was excluded." in out


def test_generate_filtering_one_layer_filter_param(caplog: pytest.LogCaptureFixture) -> None:
    # Prepare
    farn_dict_file = Path("test_farnDict_one_layer_filter_param")
    sampled_file = Path(f"sampled.{farn_dict_file.name}")
    _ = run_farn(farn_dict_file, sample=True)
    caplog.clear()
    # Execute
    _ = run_farn(sampled_file, generate=True)
    out: str = caplog.text.rstrip()
    # Assert
    assert Path("cases_one_layer").exists()
    assert "Successfully created 2 paramDict files in 2 case folders." in out


def test_sample_filtering_two_layers_filter_layer(caplog: pytest.LogCaptureFixture) -> None:
    # Prepare
    farn_dict_file = Path("test_farnDict_two_layers_filter_layer")
    # Execute
    _ = run_farn(farn_dict_file, sample=True)
    out: str = caplog.text.rstrip()
    # Assert
    assert "Successfully listed 3 valid cases. 6 invalid cases were excluded." in out


def test_generate_filtering_two_layers_filter_layer(caplog: pytest.LogCaptureFixture) -> None:
    # Prepare
    farn_dict_file = Path("test_farnDict_two_layers_filter_layer")
    sampled_file = Path(f"sampled.{farn_dict_file.name}")
    _ = run_farn(farn_dict_file, sample=True)
    caplog.clear()
    # Execute
    _ = run_farn(sampled_file, generate=True)
    out: str = caplog.text.rstrip()
    # Assert
    # case folder 'layer1_0/layers_0' must not exist
    assert not Path("cases_two_layers/layer1_0/layers_0").exists()
    assert "Successfully listed 3 valid cases. 6 invalid cases were excluded." in out
    assert "Successfully created 6 case folders." in out
    assert "Successfully created 3 paramDict files in 3 case folders." in out


def test_sample_filtering_two_layers_filter_param(caplog: pytest.LogCaptureFixture) -> None:
    # Prepare
    farn_dict_file = Path("test_farnDict_two_layers_filter_param")
    # Execute
    _ = run_farn(farn_dict_file, sample=True)
    out: str = caplog.text.rstrip()
    # Assert
    assert "Successfully listed 3 valid cases. 6 invalid cases were excluded." in out


def test_generate_filtering_two_layers_filter_param(caplog: pytest.LogCaptureFixture) -> None:
    # Prepare
    farn_dict_file = Path("test_farnDict_two_layers_filter_param")
    sampled_file = Path(f"sampled.{farn_dict_file.name}")
    _ = run_farn(farn_dict_file, sample=True)
    caplog.clear()
    # Execute
    _ = run_farn(sampled_file, generate=True)
    out: str = caplog.text.rstrip()
    # Assert
    assert Path("cases_two_layers").exists()
    assert "Successfully created 3 paramDict files in 3 case folders." in out
