from queue import Queue
import threading
import time

from . import log

class TaskBalancer:
    def __init__(self, worker_num):
        self.worker_num = worker_num
        self.workers = []
        self._start_workers()
        self.monitor_thread = threading.Thread(target=self._monitor_workers)
        self.monitor_thread.start()

    def _start_workers(self):
        for _ in range(self.worker_num):
            queue = Queue()
            worker = threading.Thread(target=self._process_tasks, args=(queue,))
            worker.start()
            self.workers.append((worker, queue))

    def _process_tasks(self, queue):
        while True:
            task = queue.get()
            for _ in range(5):
                try:
                    task()
                except Exception as e:
                    log.error(f"Task balancer's worker failed with error: {e}")
                    log.debug("Task balancer's worker will retry the task after 3 second.")
                    time.sleep(3)
                    continue
                finally:
                    queue.task_done()
                    break

    def _monitor_workers(self):
        while True:
            for worker, queue in self.workers:
                if not worker.is_alive():
                    self.workers.remove((worker, queue))
                    log.error(f"Task balancer's worker {worker.name} has failed, starting a new worker")
                    self._start_workers()
            time.sleep(5)

    def add_task(self, task):
        min_queue = min(self.workers, key=lambda x: x[1].qsize())[1]
        min_queue.put(task)

    def get_loading(self):
        return [(worker.name, queue.qsize()) for worker, queue in self.workers]
    
    def get_worker_num(self):
        return len(self.workers)
    
    def get_queue_size(self):
        return sum(queue.qsize() for worker, queue in self.workers)

