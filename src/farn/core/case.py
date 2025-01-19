# pyright: reportUnknownMemberType=false
# ruff: noqa: N806
from __future__ import annotations

import logging
import re
import sys
from collections.abc import MutableMapping, MutableSequence, Sequence
from copy import deepcopy
from enum import IntEnum
from pathlib import Path
from typing import (
    Any,
)

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

    def __init__(  # noqa: PLR0913
        self,
        case: str = "",
        layer: str = "",
        level: int = 0,
        no_of_samples: int = 0,
        index: int = 0,
        path: Path | None = None,
        *,
        is_leaf: bool = False,
        condition: MutableMapping[str, str] | None = None,
        parameters: MutableSequence[Parameter] | None = None,
        command_sets: MutableMapping[str, list[str]] | None = None,
    ) -> None:
        self.case: str | None = case
        self.layer: str | None = layer
        self.level: int = level
        self.no_of_samples: int = no_of_samples
        self.index: int = index
        self.path: Path = path or Path.cwd()
        self.is_leaf: bool = is_leaf
        self.condition: MutableMapping[str, str] = condition or {}
        self.parameters: MutableSequence[Parameter] = parameters or []
        self.command_sets: MutableMapping[str, list[str]] = command_sets or {}
        self.status: CaseStatus = CaseStatus.NONE

    @property
    def is_valid(self) -> bool:
        """Evaluates whether the case matches the configured filter expression.

        A case is considered valid if it fulfils the filter citeria
        configured in the farn dict file for the respective layer.

        Returns
        -------
        bool
            result of validity check. True indicates the case is valid, False not valid.
        """
        # Check whether the '_condition' element is defined.  Without it, case is in any case considered valid.
        if not self.condition:
            return True

        # Check whether filter expression is defined.
        # If filter expression is missing, condition cannot be evaluated but case is, by default,
        # still considered valid.
        filter_expression = self.condition.get("_filter", None)
        if not filter_expression:
            logger.warning(
                f"Layer {self.layer}: _condition element found but no _filter element defined therein. "
                f"As the filter expression is missing, the condition cannot be evalued. "
                f"Case {self.case} is hence considered valid."
            )
            return True

        # Check whether optional argument '_action' is defined. Use default action, if not.
        action = self.condition.get("_action", None)
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

        # transfer a white list of case properties to frame.f_locals for subsequent filtering
        available_vars: set[str] = set()
        for attribute in dir(self):
            try:
                if attribute in [
                    "case",
                    "layer",
                    "level",
                    "index",
                    "pathis_leaf",
                    "no_of_samples",
                    "condition",
                    "command_sets",
                ]:
                    sys._getframe().f_locals[attribute] = eval(f"self.{attribute}")  # noqa: S307, SLF001  # type: ignore[reportPrivateUsage]
                    available_vars.add(attribute)
            except Exception:  # noqa: PERF203
                logger.exception(
                    f"Layer {self.layer}, case {self.case} validity check: case {self.case} is invalid: "
                    f"Reading case property '{attribute}' failed."
                )
                return False

        # Read all parameter names and their associated values defined in current case
        # and assign them to local in-memory variables.
        for parameter in self.parameters:
            if parameter.name and not re.match("^_", parameter.name):
                try:
                    sys._getframe().f_locals[parameter.name] = parameter.value  # noqa: SLF001  # type: ignore[reportPrivateUsage]
                    available_vars.add(parameter.name)
                except Exception:
                    logger.exception(
                        f"Layer {self.layer}, case {self.case} validity check: case {self.case} is invalid: "
                        f"Reading parameter {parameter.name} with value {parameter.value} failed. "
                    )
                    return False

        logger.debug(
            f"Layer {self.layer}, available filter variables in current scope: {'{' + ', '.join(available_vars) + '}'}"
        )

        # Evaluate filter expression
        filter_expression_evaluates_to_true = False
        try:
            filter_expression_evaluates_to_true = eval(filter_expression)  # noqa: S307
        except Exception:  # noqa: BLE001
            # In case evaluation of the filter expression fails, processing will not stop.
            # However, a warning will be logged and the respective case will be considered valid.
            logger.warning(
                f"Layer {self.layer}, case {self.case} evaluation of the filter expression failed:\n"
                f"\tOne or more of the variables used in the filter expression are not defined "
                f"or not accessible in the current layer.\n"
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

    def add_parameters(
        self,
        parameters: MutableSequence[Parameter] | MutableMapping[str, str] | None = None,
    ) -> None:
        """Manually add extra parameters."""
        if isinstance(parameters, MutableSequence):
            self.parameters.extend(parameters)

        elif isinstance(parameters, MutableMapping):
            self.parameters.extend(
                Parameter(parameter_name, parameter_value) for parameter_name, parameter_value in parameters.items()
            )

        else:
            logger.error(
                f"Layer {self.layer}, case {self.case} add_parameters failed:\n"
                f"\tWrong input data format for additional parameters.\n"
            )

        return

    def to_dict(self) -> dict[str, Any]:
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

    def __str__(self) -> str:
        return str(self.to_dict())

    def __eq__(self, other: object) -> bool:
        return str(self) == str(other)


class Cases(list[Case]):
    """Container Class for Cases.

    Inherits from List[Case] and can hence be transparently used as a Python list type.
    However, Cases extends its list base class by two convenience methods:
    to_pandas() and to_numpy(), which turn the list of Case objects
    into a pandas DataFrame or numpy ndarray, respectively.
    """

    def add_parameters(
        self,
        parameters: MutableSequence[Parameter] | MutableMapping[str, str] | None = None,
    ) -> None:
        """Manually add extra parameters."""
        _cases: list[Case] = deepcopy(self)
        for case in _cases:
            case.add_parameters(parameters)

        return

    def to_pandas(
        self,
        *,
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
        indices: list[int] = []

        _cases: list[Case] = deepcopy(self)
        for _index, case in enumerate(_cases):
            indices.append(_index)
            case.path = relative_path(Path.cwd(), case.path)
            if case.parameters:
                for parameter in case.parameters:
                    if not parameter.name:
                        parameter.name = "NA"

        series: dict[str, Series] = {  # pyright: ignore[reportMissingTypeArgument]
            "case": Series(data=None, dtype=np.dtype(str), name="case"),
            "path": Series(data=None, dtype=np.dtype(str), name="path"),
        }

        for _index, case in enumerate(_cases):
            # TODO @CLAROS: Check whether we can replace .loc[_index] with .iloc[_index]
            #      and .loc[_index] with .at[_index]
            #      CLAROS, 2024-10-24
            if case.case:
                series["case"].loc[_index] = case.case  # type: ignore[call-overload, reportCallIssue]
            series["path"].loc[_index] = str(case.path)  # type: ignore[call-overload, reportCallIssue]
            if case.parameters:
                for parameter in case.parameters:
                    if parameter.name not in series:
                        if parameter.dtype is not None:
                            series[parameter.name] = Series(
                                data=None,
                                dtype=parameter.dtype,
                                name=parameter.name,
                            )
                        else:
                            series[parameter.name] = Series(
                                data=None,
                                name=parameter.name,
                            )

                    if parameter.value is not None:
                        series[parameter.name].loc[_index] = parameter.value  # type: ignore[call-overload, reportCallIssue]

        if parameters_only:
            _ = series.pop("case")
            if not use_path_as_index:
                _ = series.pop("path")

        df_X = DataFrame(data=series)

        if use_path_as_index:
            df_X = df_X.set_index("path")

        return df_X

    def to_numpy(self) -> ndarray[tuple[int, int], np.dtype[np.float64]]:
        """Return parameter values of all cases as a 2-dimensional numpy array.

        Returns
        -------
        ndarray[tuple[int, int], np.dtype[np.float64 | np.int32]]
            2-dimensional numpy array with case specific parameter values of all cases.
        """
        df_X: DataFrame = self.to_pandas(parameters_only=True)
        array: ndarray[tuple[int, int], np.dtype[np.float64]] = df_X.to_numpy().astype(np.float64)
        return array

    def filter(
        self,
        levels: int | Sequence[int] = -1,
        *,
        valid_only: bool = True,
    ) -> Cases:
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
        _levels: list[int] = [levels] if isinstance(levels, int) else list(levels)
        filtered_cases: list[Case]
        filtered_cases = [case for case in self if case.level in _levels or (case.is_leaf and -1 in _levels)]

        if valid_only:
            filtered_cases = [case for case in filtered_cases if case.is_valid]

        return Cases(filtered_cases)
