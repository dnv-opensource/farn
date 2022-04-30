import logging
import sys
from pathlib import Path
from typing import Union

__all__ = ['configure_logging']

logger = logging.getLogger(__name__)


def configure_logging(
    log_level_console: str = 'WARNING',
    log_file: Union[Path, None] = None,
    log_level_file: str = 'WARNING',
):                                          # sourcery skip: extract-duplicate-method

    log_level_console_numeric = getattr(logging, log_level_console.upper(), None)
    if not isinstance(log_level_console_numeric, int):
        raise ValueError(f'Invalid log level to console: {log_level_console_numeric}')

    log_level_file_numeric = getattr(logging, log_level_file.upper(), None)
    if not isinstance(log_level_file_numeric, int):
        raise ValueError(f'Invalid log level to file: {log_level_file_numeric}')

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level_console_numeric)
    console_formatter = logging.Formatter('%(levelname)-8s %(message)s')
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    if log_file:
        if not log_file.parent.exists():
            log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(str(log_file.absolute()), 'a')
        file_handler.setLevel(log_level_file_numeric)
        file_formatter = logging.Formatter(
            '%(asctime)s %(levelname)-8s %(message)s', '%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

    return


def plural(count: int, string: str = '') -> str:
    """conditionally returns the singular or plural form of the passed in string.

    Parameters
    ----------
    count : int
        used to determine whether singular or plural form of string shall be returned. Could i.e. be length of an iterable. If count > 1, plural form will be returned, else singular.
    string : str, optional
        the string to be returned in its singular or plural form, by default ''

    Returns
    -------
    str
        the singular or plural form of the passed in string (depending on count)
    """
    # The approach used here is a simple mapping.
    # A more sophisticated approach in future could be: nltk -> load corpus -> stem -> pluralize

    mappings = [
        ('', 's'),       # default / fallback
        ('is', 'are'),
        ('was', 'were')
    ]

    # Select the first mapping which contains the passed in string. Use mappings[0] as default / fallback.
    mapping = next((m for m in mappings if string in m), mappings[0])

    # Return singular or plural form of passed in string, depending on count
    return mapping[0] if count <= 1 else mapping[1]
