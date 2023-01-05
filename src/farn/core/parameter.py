import logging
from typing import Union

__ALL__ = ["Parameter"]

logger = logging.getLogger(__name__)


class Parameter:
    """Dataclass holding the parameter attributes 'name' and 'value'."""

    def __init__(
        self,
        name: str = "",
        value: Union[float, None] = None,
    ):
        self.name: str = name
        self.value: Union[float, None] = value
