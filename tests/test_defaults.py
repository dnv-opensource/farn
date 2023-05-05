# pyright: reportUnknownMemberType=false
from copy import deepcopy
from pathlib import Path
from typing import Any, List, Tuple

import numpy as np
from dictIO import CppDict, DictReader
from dictIO.utils.path import relative_path
from numpy import ndarray
from pandas import DataFrame

from farn import create_cases, create_samples, run_farn
from farn.core import Case, Cases, Parameter

def test_distribute_default_parameters():
    # Prepare
    farn_dict_file = Path("test_farnDict_distribute")
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
    
    assert param_dict['param0'] == 0.
    assert param_dict['param1'] == 1.
    assert param_dict['param2'] == 2.
