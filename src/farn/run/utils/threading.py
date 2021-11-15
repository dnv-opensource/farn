import logging
from queue import Queue
from threading import Thread


logger = logging.getLogger(__name__)


class Worker(Thread):
    """Worker thread executing jobs from the job queue.
    """

    # Override constructor of Thread class
    def __init__(self, queue):
        Thread.__init__(self)   # invoke base class constructor
        self.queue = queue
        self.daemon = True
        self.start()

    # Override run() method of Thread class
    def run(self):
        while True:
            try:
                func, args, kwargs = self.queue.get()
                func(*args, **kwargs)
            except Exception:
                logger.exception('Worker: Exeption raised in worker thread.')
            finally:
                self.queue.task_done()


class JobQueue(Queue):
    """JobQueue extends threading.Queue, overriding its 'put' method to accept a generic list of arguments.
    """

    def put(self, func, *args, **kwargs):
        super().put((func, args, kwargs))
