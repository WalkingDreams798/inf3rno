"""Thread pool manager for brute-force operations."""

import threading
import queue
from typing import Callable, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed


class ThreadPool:
    """Thread pool manager with queue-based task distribution."""

    def __init__(self, threads: int = 5):
        self.threads = threads
        self.task_queue = queue.Queue()
        self.results = []
        self.lock = threading.Lock()
        self.stop_event = threading.Event()

    def add_task(self, task: Any):
        """Add a task to the queue."""
        self.task_queue.put(task)

    def add_tasks(self, tasks: list):
        """Add multiple tasks to the queue."""
        for task in tasks:
            self.task_queue.put(task)

    def worker(self, func: Callable):
        """Worker function that processes tasks."""
        while not self.stop_event.is_set():
            try:
                task = self.task_queue.get(timeout=1)
            except queue.Empty:
                break

            try:
                result = func(task)
                with self.lock:
                    self.results.append(result)
            except Exception as e:
                pass
            finally:
                self.task_queue.task_done()

    def execute(self, func: Callable) -> list:
        """Execute function on all tasks using thread pool."""
        threads = []
        for _ in range(self.threads):
            t = threading.Thread(target=self.worker, args=(func,), daemon=True)
            t.start()
            threads.append(t)

        self.task_queue.join()
        self.stop_event.set()

        for t in threads:
            t.join()

        return self.results

    def reset(self):
        """Reset the thread pool for reuse."""
        while not self.task_queue.empty():
            try:
                self.task_queue.get_nowait()
            except queue.Empty:
                break
        self.results.clear()
        self.stop_event.clear()


class FuturesPool:
    """Alternative implementation using concurrent.futures."""

    def __init__(self, threads: int = 5):
        self.threads = threads

    def execute(self, func: Callable, tasks: list) -> list:
        """Execute function on all tasks and return results."""
        results = []
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {executor.submit(func, task): task for task in tasks}
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception:
                    pass
        return results
