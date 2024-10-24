import logging
import re
import subprocess as sub
from pathlib import Path
from threading import Lock

from psutil import Process

logger = logging.getLogger(__name__)

# Lock for operations that are not intrinsically thread safe
lock = Lock()


def execute_in_sub_process(
    command: str,
    path: Path | None = None,
    timeout: int | None = 7200,  # 2 hours
) -> tuple[bytes, bytes]:
    """Create a subprocess with cwd = path and executes the given shell command.
    The subprocess runs asyncroneous. The calling thread waits until the subprocess returns
    or until timeout is exceeded.
    If the subprocess has not returned after [timeout] seconds, the subprocess gets killed.
    """
    path = path or Path.cwd()

    # Configure and start subprocess in workDir (this part shall be atomic, hence secured by lock)
    with lock:
        command = re.sub(r"(^\'|\'$)", "", command)

        args = re.split(r"\s+", command.strip())

        sub_process = sub.Popen(  # noqa: S602
            args,
            stdout=sub.PIPE,
            stderr=sub.PIPE,
            shell=True,
            cwd=f"{path}",
        )

        log_string: str
        # NOTE: 18 as max string length is chosen arbitrarily.
        #       Purpose simply is to limit the length of the log string
        #       to what can practically be displayed in one line in a log console.
        max_log_string_length: int = 18
        if len(command) > max_log_string_length:
            log_string = '"' + "".join(list(command)[:11]) + ".." + "".join(list(command)[-3:]) + '"'
        else:
            log_string = f'"{command}"'

        logger.info(f"Execute {log_string:18} in {path}")
        logger.debug(f"(timout: {timeout}, pid: %{sub_process.pid})")

    # Wait for subprocess to finish
    stdout = b""
    stderr = b""
    try:
        stdout, stderr = sub_process.communicate(timeout=timeout)
    except sub.TimeoutExpired:
        logger.warning(f"Execution timeout, killing process {sub_process.pid}")
        # kill subprocess
        try:
            parent = Process(sub_process.pid)  # look if the pid still exists
            for child in parent.children(recursive=True):  # raise exeption w/o termination
                child.kill()
            parent.kill()
        except Exception:  # noqa: BLE001
            logger.warning(f"Process {sub_process.pid} non-existent. Perhaps previously terminated?")

    _log_subprocess_output(command, path, stdout, stderr)

    return (stdout, stderr)


def _log_subprocess_output(command: str, path: Path, stdout: bytes, stderr: bytes) -> None:
    if out := str(stdout, encoding="utf-8"):
        _log_subprocess_log(command, path, out)

    if err := str(stderr, encoding="utf-8"):
        _log_subprocess_log(command, path, err)


def _log_subprocess_log(command: str, path: Path, log: str) -> None:
    if re.search("error", log, re.IGNORECASE):
        logger.error(f"during execution of {command} in {path}\n{log}")
    elif re.search("warning", log, re.IGNORECASE):
        logger.warning(f"from execution of {command} in {path}\n{log}")
    elif re.search("info", log, re.IGNORECASE):
        logger.info(f"from execution of {command} in {path}\n{log}")
    elif re.search("debug", log, re.IGNORECASE):
        logger.debug(f"from execution of {command} in {path}\n{log}")
