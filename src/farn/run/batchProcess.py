import logging
from pathlib import Path

from farn.run.subProcess import execute_in_sub_process
from farn.run.utils.threading import JobQueue, Worker
from psutil import cpu_count


logger = logging.getLogger(__name__)


class AsyncBatchProcessor():

    def __init__(
        self,
        case_list_file: Path,
        command: str,
        timeout: int = 3600,
        max_number_of_cpus: int = 0,
    ):
        self.case_list_file: Path = case_list_file
        self.command: str = command
        self.timeout: int = timeout
        self.max_number_of_cpus: int = max_number_of_cpus

    def run(self):

        # Check whether caselist file exists
        if not self.case_list_file.is_file():
            logger.error(f'AsyncBatchProcessor: File {self.case_list_file} not found.')
            return

        # Read the case list and fill job queue
        cases = []
        with open(self.case_list_file, 'r') as f:
            cases = f.readlines()

        jobs = JobQueue()

        for index, path in enumerate(cases):
            path = path.strip()
            jobs.put(execute_in_sub_process, self.command, path, self.timeout)
            logger.info('Job %g queued in %s' % (index, path))  # 1

        number_of_cpus = cpu_count()
        if self.max_number_of_cpus:
            number_of_cpus = min(number_of_cpus, int(self.max_number_of_cpus))

        # Create worker threads that execute the jobs
        # (threadPool being a simple list of threads, nothing sophisticated)
        thread_pool = [Worker(jobs) for _ in range(number_of_cpus)]

        logger.info(f'AsyncBatchProcessor: started {len(thread_pool):2d} worker threads.')

        # Wait until all jobs are done
        jobs.join()

        # exit(0)
