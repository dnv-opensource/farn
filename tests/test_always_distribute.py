# pyright: reportUnknownMemberType=false
from pathlib import Path

from dictIO import CppDict, DictReader

from farn import run_farn


def test_always_distribute_parameters():
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
    param_dict: CppDict = DictReader.read(param_dict_file, comments=False)

    assert param_dict["param0"] == 0.0
    assert param_dict["param1"] == 1.0
    assert param_dict["param2"] == 2.0
