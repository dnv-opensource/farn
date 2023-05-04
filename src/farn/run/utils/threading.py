import logging
from queue import Queue
from threading import Thread
from typing import Any, Mapping, Sequence, Tuple

logger = logging.getLogger(__name__)


class JobQueue(Queue[Tuple[Any, Sequence[Any], Mapping[str, Any]]]):
    """JobQueue extends threading.Queue, overriding its 'put' method to accept a generic list of arguments."""

    def put(self, func: Any, *args: Any, **kwargs: Any):  # pyright: ignore
        """Put a callable object (function) in the JobQueue.

        Additional positional and keyword arguments provided with *args and *kwargs
        will be passed forward to the called function.

        Parameters
        ----------
        func : Any
            the callable object (function)
        """
        super().put(item=(func, args, kwargs))


class Worker(Thread):
    """Worker thread executing jobs from a job queue."""

    # Override constructor of Thread class
    def __init__(self, job_queue: JobQueue):
        """Instantiate a Worker and bind it to the passed in JobQueue instance.

        Parameters
        ----------
        job_queue : JobQueue
            the JobQueue this Worker shall be bound to
        """
        Thread.__init__(self)  # invoke base class constructor
        self.job_queue: JobQueue = job_queue
        self.daemon: bool = True
        self.start()

    # Override run() method of Thread class
    def run(self):
        """Run the next job from the JobQueue this Worker is bound to."""
        while True:
            try:
                func, args, kwargs = self.job_queue.get()
                func(*args, **kwargs)
            except Exception:
                logger.exception("Worker: Exeption raised in worker thread.")
            finally:
                self.job_queue.task_done()
