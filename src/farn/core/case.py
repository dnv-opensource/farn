# pyright: reportUnknownMemberType=false
import logging
import re
from copy import deepcopy
from enum import IntEnum
from pathlib import Path
from typing import Any, Dict, List, MutableMapping, MutableSequence, Sequence, Set, Union

import numpy as np
from dictIO.utils.path import relative_path
from numpy import ndarray
from pandas import DataFrame, Series

from farn.core import Parameter

__ALL__ = [
    "CaseStatus",
    "Case",
    "Cases",
]

logger = logging.getLogger(__name__)


class CaseStatus(IntEnum):
    """Enumeration class allowing an algorithm that processes cases, i.e. a simulator or case processor,
    to indicate the state a case iscurrently in.
    """

    NONE = 0
    FAILURE = 1
    PREPARED = 10
    RUNNING = 20
    SUCCESS = 30


class Case:
    """Dataclass holding case attributes.

    Case holds all relevant attributes needed by farn to process cases, e.g.
        - condition
        - parameter names and associated values
        - commands
        - ..
    """

    def __init__(
        self,
        case: str = "",
        layer: str = "",
        level: int = 0,
        no_of_samples: int = 0,
        index: int = 0,
        path: Union[Path, None] = None,
        is_leaf: bool = False,
        condition: Union[MutableMapping[str, str], None] = None,
        parameters: Union[MutableSequence[Parameter], None] = None,
        command_sets: Union[MutableMapping[str, List[str]], None] = None,
    ):
        self.case: Union[str, None] = case
        self.layer: Union[str, None] = layer
        self.level: int = level
        self.no_of_samples: int = no_of_samples
        self.index: int = index
        self.path: Path = path or Path.cwd()
        self.is_leaf: bool = is_leaf
        self.condition: MutableMapping[str, str] = condition or {}
        self.parameters: MutableSequence[Parameter] = parameters or []
        self.command_sets: MutableMapping[str, List[str]] = command_sets or {}
        self.status: CaseStatus = CaseStatus.NONE

    @property
    def is_valid(self) -> bool:
        """Evaluates whether the case matches the configured filter expression.

        A case is considered valid if it fulfils the filter citeria configured in farnDict for the respective layer.

        Returns
        -------
        bool
            result of validity check. True indicates the case is valid, False not valid.
        """

        # Check whether the '_condition' element is defined.  Without it, case is in any case considered valid.
        if not self.condition:
            return True

        # Check whether filter expression is defined.
        # If filter expression is missing, condition cannot be evaluated but case is, by default, still considered valid.
        filter_expression = self.condition["_filter"] if "_filter" in self.condition else None
        if not filter_expression:
            logger.warning(
                f"Layer {self.layer}: _condition element found but no _filter element defined therein. "
                f"As the filter expression is missing, the condition cannot be evalued. Case {self.case} is hence considered valid. "
            )
            return True

        # Check whether optional argument '_action' is defined. Use default action, if not.
        action = self.condition["_action"] if "_action" in self.condition else None
        if not action:
            logger.warning(
                f"Layer {self.layer}: No _action defined in _condition element. Default action 'exclude' is used. "
            )
            action = "exclude"

        # Check for formal errors that lead to invalidity
        if not self.parameters:
            logger.warning(
                f"Layer {self.layer}, case {self.case} validity check: case {self.case} is invalid: "
                f"A filter expression {filter_expression} is defined, but no parameters exist. "
            )
            return False
        for parameter in self.parameters:
            if not parameter.name:
                logger.warning(
                    f"Layer {self.layer}, case {self.case} validity check: case {self.case} is invalid: "
                    f"A filter expression {filter_expression} is defined, "
                    f"but at least one parameter name is missing. "
                )
                return False
            if not parameter.value:
                logger.warning(
                    f"Layer {self.layer}, case {self.case} validity check: case {self.case} is invalid: "
                    f"A filter expression {filter_expression} is defined and parameter names exist, "
                    f"but parameter values are missing. "
                    f"Parameter name: {parameter.name} "
                    f"Parameter value: None "
                )
                return False

        # transfer a white list of case properties to locals() for subsequent filtering
        available_vars: Set[str] = set()
        for attribute in dir(self):
            try:
                if attribute in [
                    "case",
                    "layer",
                    "level",
                    "index",
                    "path" "is_leaf",
                    "no_of_samples",
                    "condition",
                    "command_sets",
                ]:
                    locals()[attribute] = eval(f"self.{attribute}")
                    available_vars.add(attribute)
            except Exception:
                logger.exception(
                    f"Layer {self.layer}, case {self.case} validity check: case {self.case} is invalid: "
                    f"Reading case property '{attribute}' failed."
                )
                return False

        # Read all parameter names and their associated values defined in current case, and assign them to local in-memory variables
        for parameter in self.parameters:
            if parameter.name and not re.match("^_", parameter.name):
                try:
                    exec(f"{parameter.name} = {parameter.value}")
                    available_vars.add(parameter.name)
                except Exception:
                    logger.exception(
                        f"Layer {self.layer}, case {self.case} validity check: case {self.case} is invalid: "
                        f"Reading parameter {parameter.name} with value {parameter.value} failed. "
                    )
                    return False

        logger.debug(
            f"Layer {self.layer}, available filter variables in current scope: {'{'+', '.join(available_vars)+'}'}"
        )

        # Evaluate filter expression
        filter_expression_evaluates_to_true = False
        try:
            filter_expression_evaluates_to_true = eval(filter_expression)
        except Exception:
            # In case evaluation of the filter expression fails, processing will not stop.
            # However, a warning will be logged and the respective case will be considered valid.
            logger.warning(
                f"Layer {self.layer}, case {self.case} evaluation of the filter expression failed:\n"
                f"\tOne or more of the variables used in the filter expression are not defined or not accessible in the current layer.\n"
                f"\t\tLayer: {self.layer}\n"
                f"\t\tLevel: {self.level}\n"
                f"\t\tCase: {self.case}\n"
                f"\t\tFilter expression: {filter_expression}\n"
                f"\t\tParameter names: {[parameter.name for parameter in self.parameters]}\n"
                f"\t\tParameter values: {[parameter.value for parameter in self.parameters]} "
            )

        # Finally: Determine case validity based on filter expression and action
        if action == "exclude":
            if filter_expression_evaluates_to_true:
                logger.debug(
                    f"Layer {self.layer}, case {self.case} validity check: case {self.case} is invalid:\n"
                    f"\tThe filter expression '{filter_expression}' evaluated to True.\n"
                    f"\tAction '{action}' performed. Case {self.case} excluded."
                )
                return False
            return True
        if action == "include":
            if filter_expression_evaluates_to_true:
                logger.debug(
                    f"Layer {self.layer}, case {self.case} validity check: case {self.case} is valid:\n"
                    f"\tThe filter expression '{filter_expression}' evaluated to True.\n"
                    f"\tAction '{action}' performed. Case {self.case} included."
                )
                return True
            return False

        return True

    def to_dict(self) -> Dict[str, Any]:
        """Return a dict with all case attributes.

        Returns
        -------
        Dict[str, Any]
            dict with all case attributes
        """
        return {
            "case": self.case,
            "layer": self.layer,
            "level": self.level,
            "index": self.index,
            "path": self.path,
            "is_leaf": self.is_leaf,
            "no_of_samples": self.no_of_samples,
            "condition": self.condition,
            "parameters": {parameter.name: parameter.value for parameter in self.parameters or []},
            "commands": self.command_sets,
            "status": self.status,
        }

    def __str__(self):
        return str(self.to_dict())

    def __eq__(self, __o: object) -> bool:
        return str(self) == str(__o)


class Cases(List[Case]):
    """Container Class for Cases.

    Inherits from List[Case] and can hence be transparently used as a Python list type.
    However, Cases extends its list base class by two convenience methods:
    to_pandas() and to_numpy(), which turn the list of Case objects
    into a pandas DataFrame or numpy ndarray, respectively.
    """

    def to_pandas(
        self,
        use_path_as_index: bool = True,
        parameters_only: bool = False,
    ) -> DataFrame:
        """Return cases as a pandas Dataframe.

        Returns a DataFrame with case properties and case specific parameter values of all cases.

        Parameters
        ----------
        use_path_as_index : bool, optional
            turn path column into index column, by default True
        parameters_only : bool, optional
            reduce DataFrame to contain only the case's parameter values, by default False

        Returns
        -------
        DataFrame
            DataFrame with case properties and case specific parameter values of all cases.
        """
        indices: List[int] = []

        _cases: List[Case] = deepcopy(self)
        for _index, case in enumerate(_cases):
            indices.append(_index)
            case.path = relative_path(Path.cwd(), case.path)
            if case.parameters:
                for parameter in case.parameters:
                    if not parameter.name:
                        parameter.name = "NA"

        series: Dict[str, Series] = {  # pyright: ignore
            "case": Series(data=None, dtype=np.dtype(str), name="case"),
            "path": Series(data=None, dtype=np.dtype(str), name="path"),
        }

        for _index, case in enumerate(_cases):
            if case.case:
                series["case"].loc[_index] = case.case
            series["path"].loc[_index] = str(case.path)
            if case.parameters:
                for parameter in case.parameters:
                    if parameter.name not in series:
                        series[parameter.name] = Series(data=None, dtype=parameter.dtype, name=parameter.name)
                    if parameter.value is not None:
                        series[parameter.name].loc[_index] = parameter.value

        if parameters_only:
            _ = series.pop("case")
            if not use_path_as_index:
                _ = series.pop("path")

        df_X = DataFrame(data=series)  # noqa: N806

        if use_path_as_index:
            df_X.set_index("path", inplace=True)

        return df_X

    def to_numpy(self) -> ndarray[Any, Any]:
        """Return parameter values of all cases as a 2-dimensional numpy array.

        Returns
        -------
        ndarray[Any, Any]
            2-dimensional numpy array with case specific parameter values of all cases.
        """
        df_X: DataFrame = self.to_pandas(parameters_only=True)  # noqa: N806
        array: ndarray[Any, Any] = df_X.to_numpy()
        return array

    def filter(
        self,
        levels: Union[int, Sequence[int]] = -1,
        valid_only: bool = True,
    ) -> "Cases":
        """Return a sub-set of cases according to the passed in selection criteria.

        Parameters
        ----------
        levels : Union[int, Sequence[int]], optional
            return all cases of a distinct level, or a sequence of levels.
            level=-1 returns the last level (the leaf cases), by default -1
        valid_only : bool, optional
            return only valid cases, i.e cases which pass a filter expression
            defined for the case's layer, by default True

        Returns
        -------
        Cases
            Cases object containing all cases that match the selection criteria.
        """
        _levels: List[int] = [levels] if isinstance(levels, int) else list(levels)
        filtered_cases: List[Case]
        filtered_cases = [case for case in self if case.level in _levels or (case.is_leaf and -1 in _levels)]

        if valid_only:
            filtered_cases = [case for case in filtered_cases if case.is_valid]

        return Cases(filtered_cases)
