import logging
from collections.abc import Callable, Mapping, Sequence
from queue import Queue
from threading import Thread
from typing import Any

logger = logging.getLogger(__name__)


class JobQueue(Queue[tuple[Any, Sequence[Any], Mapping[str, Any]]]):
    """Queue for jobs to be executed by worker threads.

    JobQueue extends `threading.Queue`.
    It provides an additional `put_callable()` method, allowing to put
    a callable with a generic list of arguments in the queue.
    """

    def put_callable(
        self,
        func: Callable[..., Any],
        *args: Any,  # noqa: ANN401
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        """Put a callable object (function) in the JobQueue.

        Additional positional and keyword arguments provided with args and kwargs
        will be passed on to the called function.

        Parameters
        ----------
        func : Any
            the callable object (function)
        """
        super().put(item=(func, args, kwargs))


class Worker(Thread):
    """Worker thread executing jobs from a job queue."""

    # Override constructor of Thread class
    def __init__(self, job_queue: JobQueue) -> None:
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
    def run(self) -> None:
        """Run the next job from the JobQueue this Worker is bound to."""
        while True:
            try:
                func, args, kwargs = self.job_queue.get()
                func(*args, **kwargs)
            except Exception:  # noqa: PERF203
                logger.exception("Worker: Exeption raised in worker thread.")
            finally:
                self.job_queue.task_done()
