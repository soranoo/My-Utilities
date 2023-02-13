from queue import Queue
import threading
import time

from . import log

class TaskBalancer:
    def __init__(self, worker_num):
        self.worker_num = worker_num
        self.queue = Queue()
        self.workers = []
        self._start_workers()
        self.monitor_thread = threading.Thread(target=self._monitor_workers)
        self.monitor_thread.start()

    def _start_workers(self):
        for i in range(self.worker_num):
            worker = threading.Thread(target=self._process_tasks)
            worker.start()
            self.workers.append(worker)
            if i%2 == 0:
                time.sleep(0.1)

    def _process_tasks(self):
        while True:
            task = self.queue.get()
            for _ in range(5):
                try:
                    task()
                except Exception as e:
                    log.error(f"Task balancer's worker failed with error: {e}")
                    log.debug("Task balancer's worker will retry the task after 3 second.")
                    time.sleep(3)
                    continue
                finally:
                    self.queue.task_done()

    def _monitor_workers(self):
        while True:
            for worker in self.workers:
                if not worker.is_alive():
                    self.workers.remove(worker)
                    log.error(f"Task balancer's worker {worker.name} has failed, starting a new worker")
                    self._start_workers()
            time.sleep(5)

    def add_task(self, task):
        self.queue.put(task)
        
    def get_current_queue_size(self):
        return self.queue.qsize()
