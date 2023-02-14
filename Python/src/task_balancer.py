from queue import Queue
import threading
import time

from . import log

class TaskBalancer:
    """
    Task balancer is a class that can be distributed tasks to multiple threads.
    """
    def __init__(self, min_worker_num:int, max_worker_num:int, worker_idle_threshold:int = 300):
        """
        ### Parameters ###
            - `min_worker_num`(int): the minimum number of workers that the task balancer will have.
            - `max_worker_num`(int): the maximum number of workers that the task balancer will have.
            - `worker_idle_threshold`(int): the number of seconds to wait before shutting down a idle worker.
        """
        self.min_worker_num = min_worker_num
        self.max_worker_num = max_worker_num
        self.idle_threshold = worker_idle_threshold
        self.workers = []
        self._init_workers()
        self.monitor_thread = threading.Thread(target=self._monitor_workers)
        self.monitor_thread.start()

    def _init_workers(self):
        """
        ### Description ###
        Create the base number of workers for the initial state of the task balancer.
        """
        for i in range(self.min_worker_num):
            self._create_new_worker()
            if i%2 == 0:
                time.sleep(0.1)
            
    def _create_new_worker(self, queue:Queue = None):
        """
        ### Description ###
        Create a new worker thread and add it to the worker list.
        
        ### Parameters ###
            - `queue`(Queue): the queue that the worker will be processing tasks from.
        """
        queue = queue or Queue()
        worker = threading.Thread(target=self._process_tasks, args=(queue,))
        worker.start()
        self.workers.append((worker, queue))
    
    def _can_I_stop(self) -> bool:
        """
        ### Description ###
        Give a boolean value to indicate that worker can be stopped or not.
        
        ### Returns ###
            - `bool`: True if the worker can be stopped, False otherwise.
        """
        # scale down worker
        return self.get_worker_count() > self.min_worker_num

    def _process_tasks(self, queue:Queue):
        """
        ### Description ###
        Worker thread's main function. It will process tasks from the queue until the queue is empty and the worker is idle for too long.
        
        ### Parameters ###
            - `queue`(Queue): the queue that the worker will be processing tasks from.
        """
        last_activity_timestamp = time.time()
        while True:
            if queue.qsize() == 0 and (
                last_activity_timestamp + self.idle_threshold < time.time()
                and self._can_I_stop()
            ):
                self.workers.remove((threading.current_thread(), queue))
                return

            task = queue.get()

            last_activity_timestamp = time.time()

            for _ in range(5):
                try:
                    task()
                    queue.task_done()
                    break
                except Exception as e:
                    log.error(f"Task balancer's worker({threading.current_thread().name}) failed with error: {e}")
                    log.debug(f"Task balancer's worker({threading.current_thread().name}) will retry the task after 3 seconds.")
                    time.sleep(3)
                    continue

    def _monitor_workers(self):
        """
        ### Description ###
        Monitor the worker threads and scale up according to the number of tasks in the queue.
        """
        while True:
            for worker, queue in self.workers:
                if not worker.is_alive():
                    self.workers.remove((worker, queue))
                    log.error(f"Task balancer's worker {worker.name} has failed, starting a new worker")
                    self._start_workers(queue=queue)

            if self.get_remaining_task_count() > self.get_worker_count()*3 and self.get_worker_count() < self.max_worker_num:
                # Scale up
                self._create_new_worker()
                
            time.sleep(5)

    def add_task(self, task):
        """
        ### Description ###
        Add a task to the task balancer.
        
        ### Parameters ###
            - `task`(function): the task to be added.
            
        ### Example ###
            ```python
            def print_hello_world(text:str):
                print(text)
            
            task_balancer = TaskBalancer(1, 10)
            task_balancer.add_task(lambda:print_hello_world("Hello World!"))
            ```
        """
        min_queue = min(self.workers, key=lambda x: x[1].qsize())[1]
        min_queue.put(task)
    
    def get_worker_count(self) -> int:
        """
        ### Description ###
        Get the number of workers.
        
        ### Returns ###
            - `int`: the number of workers.
        """
        return len(self.workers)
    
    def get_remaining_task_count(self) -> int:
        """
        ### Description ###
        Get the number of remaining tasks.
        
        ### Returns ###
            - `int`: the number of remaining tasks.
        """
        return sum(queue.qsize() for worker, queue in self.workers)

