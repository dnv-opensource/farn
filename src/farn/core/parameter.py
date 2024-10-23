import logging

import numpy as np

__ALL__ = ["Parameter"]

logger = logging.getLogger(__name__)


class Parameter:
    """Dataclass holding the parameter attributes 'name' and 'value'."""

    def __init__(
        self,
        name: str = "",
        value: float | int | bool | str | None = None,
    ):
        self.name: str = name
        self.value: float | int | bool | str | None = value

    @property
    def type(self) -> type[float] | type[int] | type[bool] | type[str] | None:
        """Returns the Python type of the parameter.

        Returns
        -------
        Union[Type[float], Type[int], Type[bool], Type[str], None]
            the Python type
        """
        return None if self.value is None else type(self.value)

    @property
    def dtype(self) -> np.dtype[float] | np.dtype[int] | np.dtype[bool] | np.dtype[str] | None:  # type: ignore
        """Returns the numpy dtype of the parameter.

        Returns
        -------
        Union[np.dtype[float], np.dtype[int], np.dtype[bool], np.dtype[str], None]
            the numpy dtype
        """
        _type = self.type
        return None if _type is None else np.dtype(_type)  # type: ignore
