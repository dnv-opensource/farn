import os

__all__ = ["append_system_variable"]


def append_system_variable(variable: str, value: str):
    """
    append system variable depending on system
    """
    os.environ[variable] = value
    return
