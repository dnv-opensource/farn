import logging
import os
from pathlib import Path

import pytest


@pytest.fixture(scope='package', autouse=True)
def chdir():
    os.chdir(Path(__file__).parent.absolute())
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
