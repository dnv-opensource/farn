import logging
import re
import subprocess as sub
from pathlib import Path
from threading import Lock
from typing import Union

from psutil import Process


logger = logging.getLogger(__name__)

# Lock for operations that are not intrinsically thread safe
lock = Lock()


def execute_in_sub_process(command: str, path: Union[Path, None] = None, timeout: int = 3600):
    """Creates a subprocess with cwd = path and executes the given shell command.
    The subprocess runs asyncroneous. The calling thread waits until the subprocess returns or until timeout is exceeded.
    If the subprocess has not returned after [timeout] seconds, the subprocess gets killed.
    """

    path = path or Path.cwd()

    # Configure and start subprocess in workDir (this part shall be atomic, hence secured by lock)
    with lock:

        command = re.sub(r'(^\'|\'$)', '', command)

        args = re.split(r'\s+', command.strip())

        sub_process = sub.Popen(args, stdout=sub.PIPE, stderr=sub.PIPE, shell=True, cwd=f"{path}")

        if len(command) > 18:
            cmd_string = '"' + ''.join(list(command)[:11]
                                       ) + '..' + ''.join(list(command)[-3:]) + '"'
        else:
            cmd_string = '"' + command + '"'

        logger.info("Execute {:18} in {:}".format(cmd_string, path))
        logger.debug(f"(timout: {timeout}, pid: %{sub_process.pid})")

    # Wait for subprocess to finish
    stdout = bytes()
    stderr = bytes()
    try:
        stdout, stderr = sub_process.communicate(timeout=timeout)
    except sub.TimeoutExpired:
        logger.warning(f'Execution timeout, killing process {sub_process.pid:s}')
        # kill subprocess
        parent = Process(sub_process.pid)
        for child in parent.children(recursive=True):
            child.kill()
        parent.kill()

    _log_subprocess_output(command, path, stdout, stderr)

    return (stdout, stderr)


def _log_subprocess_output(command: str, path: Path, stdout: bytes, stderr: bytes):

    if out := str(stdout, encoding='utf-8'):
        _log_subprocess_log(command, path, out)

    if err := str(stderr, encoding='utf-8'):
        _log_subprocess_log(command, path, err)


def _log_subprocess_log(command: str, path: Path, log: str):

    if re.search('error', log, re.I):
        logger.error(f'during execution of {command} in {path}\n{log}')
    elif re.search('warning', log, re.I):
        logger.warning(f'from execution of {command} in {path}\n{log}')
    elif re.search('info', log, re.I):
        logger.info(f'from execution of {command} in {path}\n{log}')
    elif re.search('debug', log, re.I):
        logger.debug(f'from execution of {command} in {path}\n{log}')
