import logging
import re
import subprocess as sub
from pathlib import Path
from threading import Lock

from psutil import Process


logger = logging.getLogger(__name__)

# Lock for operations that are not intrinsically thread safe
lock = Lock()


def execute_in_sub_process(command: str, path: Path = None, timeout: int = 3600):
    """Creates a subprocess with cwd = path and executes the given shell command.
    The subprocess runs asyncroneous. The calling thread waits until the subprocess returns or until timeout is exceeded.
    If the subprocess has not returned after [timeout] seconds, the subprocess gets killed.
    """

    path = path or Path.cwd()

    # Configure and start subprocess in workDir (this part shall be atomic, hence secured by lock)
    with lock:

        args = re.sub(r'(^\'|\'$)', '', command)

        args = re.split(r'\s+', args.strip())

        sub_process = sub.Popen(
            args, stdout=sub.PIPE, stderr=sub.PIPE, shell=True, cwd=r"%s" % path
        )

        logger.info(
            f"Execute {command} in {path} (timout: {timeout}, pid: %{sub_process.pid})"
        )                                                                                   # level=1  override=False  timestamp=True

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

    str_out = str(stdout, encoding='utf-8')
    if re.search('ERROR', str_out):
        logger.warning(f'Execution of {command} failed: {str_out}')

    str_err = str(stderr, encoding='utf-8')
    if str_err != '':
        logger.warning(f'Execution of {command} failed: {str_err}')

    return (stdout, stderr)
