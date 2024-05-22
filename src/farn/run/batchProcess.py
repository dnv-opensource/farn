import logging
from pathlib import Path

from psutil import cpu_count

from farn.run.subProcess import execute_in_sub_process
from farn.run.utils.threading import JobQueue, Worker

logger = logging.getLogger(__name__)


class AsyncBatchProcessor:
    """Batch processor for asynchroneous execution of a shell command in multiple case folders."""

    def __init__(
        self,
        case_list_file: Path,
        command: str,
        timeout: int = 3600,
        max_number_of_cpus: int = 0,
    ):
        """Instantiate an asynchroneous batch processor
        to execute a shell command in multiple case folders.

        Parameters
        ----------
        case_list_file : Path
            the file containing the list of case folders the shell command shall be executed in
        command : str
            the shell command to be executed
        timeout : int, optional
            time out in  seconds, by default 3600
        max_number_of_cpus : int, optional
            number of cpus to be used, by default 0
        """
        self.case_list_file: Path = case_list_file
        self.command: str = command
        self.timeout: int = timeout
        self.max_number_of_cpus: int = max_number_of_cpus

    def run(self):
        """Run the shell command in all case folders."""

        # Check whether caselist file exists
        if not self.case_list_file.is_file():
            logger.error(f"AsyncBatchProcessor: File {self.case_list_file} not found.")
            return

        # Read the case list and fill job queue
        cases = []
        with open(self.case_list_file, "r") as f:
            cases = f.readlines()

        jobs = JobQueue()

        for index, path in enumerate(cases):
            path = path.strip()
            jobs.put(execute_in_sub_process, self.command, path, self.timeout)
            logger.info("Job %g queued in %s" % (index, path))  # 1

        number_of_cpus = cpu_count()
        if self.max_number_of_cpus:
            number_of_cpus = min(number_of_cpus, int(self.max_number_of_cpus))

        # Create worker threads that execute the jobs
        # (threadPool being a simple list of threads, nothing sophisticated)
        thread_pool = [Worker(jobs) for _ in range(number_of_cpus)]

        logger.info(f"AsyncBatchProcessor: started {len(thread_pool):2d} worker threads.")

        # Wait until all jobs are done
        jobs.join()

        # exit(0)
