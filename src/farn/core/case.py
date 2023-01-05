# pyright: reportUnknownMemberType=false
import logging
import re
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, MutableMapping, MutableSequence, Set, Union

import numpy as np
from dictIO.utils.path import relative_path
from numpy import ndarray
from pandas import DataFrame, Series

from farn.core import Parameter

__ALL__ = [
    "Case",
]

logger = logging.getLogger(__name__)


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
        """Returns a dict with all case attributes.

        Returns
        -------
        Dict[str, Any]
            dict with all case attributes
        """
        return {
            "_case": self.case,
            "_layer": self.layer,
            "_level": self.level,
            "_index": self.index,
            "_path": self.path,
            "_is_leaf": self.is_leaf,
            "_no_of_samples": self.no_of_samples,
            "_condition": self.condition,
            "_parameters": {parameter.name: parameter.value for parameter in self.parameters or []},
            "_commands": self.command_sets,
        }


class Cases(List[Case]):
    """Container for Cases.

    Inherits from list[Case] and can hence be transparently used as a Python list type.
    However, Cases extends its list base class by two convenience methods:
    to_pandas() and to_numpy(), which turn the list of Case objects
    into a pandas DataFrame or numpy ndarray, respectively.
    """

    def to_pandas(self, use_path_as_index: bool = True) -> DataFrame:

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
            "case": Series(data=None, dtype=str, name="case"),
            "path": Series(data=None, dtype=str, name="path"),
        }

        for _index, case in enumerate(_cases):
            if case.case:
                series["case"].loc[_index] = case.case
            series["path"].loc[_index] = str(case.path)
            if case.parameters:
                for parameter in case.parameters:
                    if parameter.value is not None:
                        if parameter.name not in series:
                            series[parameter.name] = Series(data=None, dtype=type(parameter.value), name=parameter.name)
                        series[parameter.name].loc[_index] = parameter.value

        df_X = DataFrame(data=series)  # noqa: N806

        if use_path_as_index:
            df_X.set_index("path", inplace=True)

        return df_X

    def to_numpy(self) -> ndarray[Any, Any]:
        df_X: DataFrame = self.to_pandas(use_path_as_index=False)  # noqa: N806
        df_X.drop(["case", "path"], axis=1, inplace=True)
        array: ndarray[Any, Any] = df_X.to_numpy(copy=True, na_value=np.nan)
        return array
