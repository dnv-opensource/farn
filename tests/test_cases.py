# pyright: reportUnknownMemberType=false
from copy import deepcopy
from pathlib import Path
from typing import Any, List, Tuple

import numpy as np
from dictIO import CppDict, DictReader
from dictIO.utils.path import relative_path
from numpy import ndarray
from pandas import DataFrame

from farn import create_cases, create_samples
from farn.core import Case, Cases, Parameter


def test_cases():
    # Prepare
    case_1, case_2, case_3 = _create_cases()
    case_list_assert: List[Case] = [case_1, case_2, case_3]
    # Execute
    cases: Cases = Cases([case_1, case_2, case_3])
    cases_by_append: Cases = Cases()
    cases_by_append.append(case_1)
    cases_by_append.append(case_2)
    cases_by_append.append(case_3)
    cases_by_extend: Cases = Cases()
    cases_by_extend.extend([case_1, case_2, case_3])
    # Assert
    assert len(cases) == 3
    assert len(cases_by_append) == 3
    assert len(cases_by_extend) == 3
    _assert_type_and_equality(cases, case_list_assert)
    _assert_type_and_equality(cases_by_append, case_list_assert)
    _assert_type_and_equality(cases_by_extend, case_list_assert)
    _assert_sequence(cases, case_1, case_2, case_3)
    _assert_sequence(cases_by_append, case_1, case_2, case_3)
    _assert_sequence(cases_by_extend, case_1, case_2, case_3)
    assert len(cases[0].parameters) == 1
    assert len(cases[1].parameters) == 2
    assert len(cases[2].parameters) == 3
    assert cases[2].parameters[0].name == "param_1"  # type: ignore
    assert cases[2].parameters[1].name == "param_2"  # type: ignore
    assert cases[2].parameters[2].name == "param_3"  # type: ignore
    assert cases[2].parameters[0].value == 31.1  # type: ignore
    assert cases[2].parameters[1].value == 32.2  # type: ignore
    assert cases[2].parameters[2].value == 33.3  # type: ignore
    assert cases[0].case == "case_1"
    assert cases[1].case == "case_2"
    assert cases[2].case == "case_3"


def _assert_type_and_equality(cases: Cases, case_list_assert: List[Case]):
    assert cases == case_list_assert
    assert isinstance(cases, List)
    assert isinstance(cases, Cases)


def _assert_sequence(cases: Cases, case_assert_1: Case, case_assert_2: Case, case_assert_3: Case):
    assert cases[0] is case_assert_1
    assert cases[1] is case_assert_2
    assert cases[2] is case_assert_3


def test_to_pandas_range_index():
    # Prepare
    case_1, case_2, case_3 = _create_cases()
    cases: Cases = Cases([case_1, case_2, case_3])
    df_assert: DataFrame = _create_dataframe(use_path_as_index=False, parameters_only=False)
    # Execute
    df: DataFrame = cases.to_pandas(use_path_as_index=False)
    # Assert
    assert df.shape == df_assert.shape
    assert df.shape == (3, 5)
    assert df.equals(df_assert)


def test_to_pandas_range_index_parameters_only():
    # Prepare
    case_1, case_2, case_3 = _create_cases()
    cases: Cases = Cases([case_1, case_2, case_3])
    df_assert: DataFrame = _create_dataframe(use_path_as_index=False, parameters_only=True)
    # Execute
    df: DataFrame = cases.to_pandas(use_path_as_index=False, parameters_only=True)
    # Assert
    assert df.shape == df_assert.shape
    assert df.shape == (3, 3)
    assert df.equals(df_assert)


def test_to_pandas_path_index():
    # Prepare
    case_1, case_2, case_3 = _create_cases()
    cases: Cases = Cases([case_1, case_2, case_3])
    df_assert: DataFrame = _create_dataframe(use_path_as_index=True, parameters_only=False)
    # Execute
    df: DataFrame = cases.to_pandas()
    # Assert
    assert df.shape == df_assert.shape
    assert df.shape == (3, 4)
    assert df.equals(df_assert)


def test_to_pandas_path_index_parameters_only():
    # Prepare
    case_1, case_2, case_3 = _create_cases()
    cases: Cases = Cases([case_1, case_2, case_3])
    df_assert: DataFrame = _create_dataframe(use_path_as_index=True, parameters_only=True)
    # Execute
    df: DataFrame = cases.to_pandas(parameters_only=True)
    # Assert
    assert df.shape == df_assert.shape
    assert df.shape == (3, 3)
    assert df.equals(df_assert)


def test_to_numpy():
    # Prepare
    case_1, case_2, case_3 = _create_cases()
    cases: Cases = Cases([case_1, case_2, case_3])
    array_assert: ndarray[Any, Any] = _create_ndarray()
    # Execute
    array: ndarray[Any, Any] = cases.to_numpy()
    # Assert
    assert array.shape == array_assert.shape
    assert array.shape == (3, 3)
    assert str(array) == str(array_assert)


def _create_cases() -> Tuple[Case, Case, Case]:
    parameter_11 = Parameter("param_1", 11.1)
    parameter_12 = Parameter("param_2", 12.2)  # noqa: F841
    parameter_13 = Parameter("param_3", 13.3)  # noqa: F841
    case_1: Case = Case(case="case_1", parameters=[parameter_11])
    parameter_21 = Parameter("param_1", 21.1)
    parameter_22 = Parameter("param_2", 22.2)
    parameter_23 = Parameter("param_3", 23.3)  # noqa: F841
    case_2: Case = Case(case="case_2", parameters=[parameter_21, parameter_22])
    parameter_31 = Parameter("param_1", 31.1)
    parameter_32 = Parameter("param_2", 32.2)
    parameter_33 = Parameter("param_3", 33.3)
    case_3: Case = Case(case="case_3", parameters=[parameter_31, parameter_32, parameter_33])
    return (case_1, case_2, case_3)


def _create_dataframe(use_path_as_index: bool, parameters_only: bool) -> DataFrame:
    cwd: Path = Path.cwd()
    path: str = str(relative_path(cwd, cwd))
    index: List[int] = [0, 1, 2]
    columns: List[str] = ["case", "path", "param_1", "param_2", "param_3"]
    values: List[List[Any]]
    values = [
        ["case_1", path, 11.1, None, None],
        ["case_2", path, 21.1, 22.2, None],
        ["case_3", path, 31.1, 32.2, 33.3],
    ]
    df: DataFrame = DataFrame(data=values, index=index, columns=columns)
    if parameters_only:
        df.drop(["case"], axis=1, inplace=True)
        if not use_path_as_index:
            df.drop(["path"], axis=1, inplace=True)
    if use_path_as_index:
        df.set_index("path", inplace=True)
    return df


def _create_ndarray() -> ndarray[Any, Any]:
    array: ndarray[Any, Any] = np.array(
        [
            [11.1, np.nan, np.nan],
            [21.1, 22.2, np.nan],
            [31.1, 32.2, 33.3],
        ]
    )
    return array


def test_filter_all():
    # Prepare
    farn_dict_file = Path("test_farnDict_exclude_filtering")
    farn_dict: CppDict = DictReader.read(farn_dict_file, comments=False)
    create_samples(farn_dict)
    case_dir: Path = Path.cwd()
    cases: Cases = create_cases(farn_dict, case_dir, valid_only=False)
    cases_not_modified_assert: Cases = deepcopy(cases)
    cases_all_assert: Cases = deepcopy(cases)
    # Execute
    cases_all: Cases = cases.filter([0, 1], valid_only=False)
    # Assert
    assert isinstance(cases_all, Cases)
    assert len(cases_all) == len(cases_all_assert)
    assert cases_all == cases_all_assert
    assert cases == cases_not_modified_assert


def test_filter_level_0():
    # Prepare
    farn_dict_file = Path("test_farnDict_exclude_filtering")
    farn_dict: CppDict = DictReader.read(farn_dict_file, comments=False)
    create_samples(farn_dict)
    case_dir: Path = Path.cwd()
    cases: Cases = create_cases(farn_dict, case_dir, valid_only=False)
    cases_not_modified_assert: Cases = deepcopy(cases)
    cases_filtered_assert: Cases = Cases([case for case in cases if case.level == 0])
    # Execute
    cases_filtered: Cases = cases.filter(0, valid_only=False)
    # Assert
    assert isinstance(cases_filtered, Cases)
    assert len(cases_filtered) == len(cases_filtered_assert)
    assert cases_filtered == cases_filtered_assert
    assert cases == cases_not_modified_assert


def test_filter_level_1():
    # Prepare
    farn_dict_file = Path("test_farnDict_exclude_filtering")
    farn_dict: CppDict = DictReader.read(farn_dict_file, comments=False)
    create_samples(farn_dict)
    case_dir: Path = Path.cwd()
    cases: Cases = create_cases(farn_dict, case_dir, valid_only=False)
    cases_not_modified_assert: Cases = deepcopy(cases)
    cases_filtered_assert: Cases = Cases([case for case in cases if case.level == 1])
    # Execute
    cases_filtered: Cases = cases.filter(1, valid_only=False)
    # Assert
    assert isinstance(cases_filtered, Cases)
    assert len(cases_filtered) == len(cases_filtered_assert)
    assert cases_filtered == cases_filtered_assert
    assert cases == cases_not_modified_assert


def test_filter_level_minus_1():
    # Prepare
    farn_dict_file = Path("test_farnDict_exclude_filtering")
    farn_dict: CppDict = DictReader.read(farn_dict_file, comments=False)
    create_samples(farn_dict)
    case_dir: Path = Path.cwd()
    cases: Cases = create_cases(farn_dict, case_dir, valid_only=False)
    cases_not_modified_assert: Cases = deepcopy(cases)
    cases_filtered_assert: Cases = Cases([case for case in cases if case.is_leaf])
    # Execute
    cases_filtered: Cases = cases.filter(-1, valid_only=False)
    # Assert
    assert isinstance(cases_filtered, Cases)
    assert len(cases_filtered) == len(cases_filtered_assert)
    assert cases_filtered == cases_filtered_assert
    assert cases == cases_not_modified_assert


def test_filter_all_valid_only():
    # Prepare
    farn_dict_file = Path("test_farnDict_exclude_filtering")
    farn_dict: CppDict = DictReader.read(farn_dict_file, comments=False)
    create_samples(farn_dict)
    case_dir: Path = Path.cwd()
    cases: Cases = create_cases(farn_dict, case_dir, valid_only=False)
    cases_not_modified_assert: Cases = deepcopy(cases)
    cases_all_assert: Cases = Cases([case for case in cases if case.is_valid])
    # Execute
    cases_all: Cases = cases.filter([0, 1], valid_only=True)
    # Assert
    assert isinstance(cases_all, Cases)
    assert len(cases_all) == len(cases_all_assert)
    assert cases_all == cases_all_assert
    assert cases == cases_not_modified_assert


def test_filter_level_0_valid_only():
    # Prepare
    farn_dict_file = Path("test_farnDict_exclude_filtering")
    farn_dict: CppDict = DictReader.read(farn_dict_file, comments=False)
    create_samples(farn_dict)
    case_dir: Path = Path.cwd()
    cases: Cases = create_cases(farn_dict, case_dir, valid_only=False)
    cases_not_modified_assert: Cases = deepcopy(cases)
    cases_filtered_assert: Cases = Cases([case for case in cases if case.level == 0 and case.is_valid])
    # Execute
    cases_filtered: Cases = cases.filter(0, valid_only=True)
    # Assert
    assert isinstance(cases_filtered, Cases)
    assert len(cases_filtered) == len(cases_filtered_assert)
    assert cases_filtered == cases_filtered_assert
    assert cases == cases_not_modified_assert


def test_filter_level_1_valid_only():
    # Prepare
    farn_dict_file = Path("test_farnDict_exclude_filtering")
    farn_dict: CppDict = DictReader.read(farn_dict_file, comments=False)
    create_samples(farn_dict)
    case_dir: Path = Path.cwd()
    cases: Cases = create_cases(farn_dict, case_dir, valid_only=False)
    cases_not_modified_assert: Cases = deepcopy(cases)
    cases_filtered_assert: Cases = Cases([case for case in cases if case.level == 1 and case.is_valid])
    # Execute
    cases_filtered: Cases = cases.filter(1, valid_only=True)
    # Assert
    assert isinstance(cases_filtered, Cases)
    assert len(cases_filtered) == len(cases_filtered_assert)
    assert cases_filtered == cases_filtered_assert
    assert cases == cases_not_modified_assert


def test_filter_level_minus_1_valid_only():
    # Prepare
    farn_dict_file = Path("test_farnDict_exclude_filtering")
    farn_dict: CppDict = DictReader.read(farn_dict_file, comments=False)
    create_samples(farn_dict)
    case_dir: Path = Path.cwd()
    cases: Cases = create_cases(farn_dict, case_dir, valid_only=False)
    cases_not_modified_assert: Cases = deepcopy(cases)
    cases_filtered_assert: Cases = Cases([case for case in cases if case.is_leaf and case.is_valid])
    # Execute
    cases_filtered: Cases = cases.filter(-1, valid_only=True)
    # Assert
    assert isinstance(cases_filtered, Cases)
    assert len(cases_filtered) == len(cases_filtered_assert)
    assert cases_filtered == cases_filtered_assert
    assert cases == cases_not_modified_assert


def test_filter_default_arguments():
    # Prepare
    farn_dict_file = Path("test_farnDict_exclude_filtering")
    farn_dict: CppDict = DictReader.read(farn_dict_file, comments=False)
    create_samples(farn_dict)
    case_dir: Path = Path.cwd()
    cases: Cases = create_cases(farn_dict, case_dir, valid_only=False)
    cases_not_modified_assert: Cases = deepcopy(cases)
    cases_filtered_assert: Cases = Cases([case for case in cases if case.is_leaf and case.is_valid])
    # Execute
    cases_filtered: Cases = cases.filter()
    # Assert
    assert isinstance(cases_filtered, Cases)
    assert len(cases_filtered) == len(cases_filtered_assert)
    assert cases_filtered == cases_filtered_assert
    assert cases == cases_not_modified_assert
