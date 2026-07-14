"""Base brute-force module."""

import threading
import queue
import time
from typing import Optional
from abc import ABC, abstractmethod
from tqdm import tqdm

from core.reporter import Reporter


class BaseBrute(ABC):
    """Base class for all brute-force modules."""

    def __init__(
        self,
        target: str,
        port: int,
        username: str,
        wordlist: str,
        threads: int = 5,
        output_file: Optional[str] = None,
        verbose: bool = False,
    ):
        self.target = target
        self.port = port
        self.username = username
        self.wordlist = wordlist
        self.threads = threads
        self.output_file = output_file
        self.verbose = verbose

        self.password_queue = queue.Queue()
        self.found = []
        self.attempts = 0
        self.total_passwords = 0
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self.reporter = Reporter(verbose=verbose, output_file=output_file)
        self.progress_bar = None

    @abstractmethod
    def try_login(self, username: str, password: str) -> bool:
        """Attempt login with given credentials. Returns True if successful."""
        pass

    def load_wordlist(self):
        """Load passwords from wordlist file into queue."""
        try:
            with open(self.wordlist, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    password = line.strip()
                    if password:
                        self.password_queue.put(password)
            self.total_passwords = self.password_queue.qsize()
            return True
        except FileNotFoundError:
            self.reporter.error(f"Wordlist not found: {self.wordlist}")
            return False

    def worker(self):
        """Worker thread for brute-force attempts."""
        while not self.stop_event.is_set():
            try:
                password = self.password_queue.get(timeout=1)
            except queue.Empty:
                break

            try:
                success = self.try_login(self.username, password)
                with self.lock:
                    self.attempts += 1
                    if self.progress_bar:
                        self.progress_bar.update(1)

                if success:
                    with self.lock:
                        self.found.append((self.username, password))
                    self.reporter.attempt(self.username, password, True)
                elif self.verbose:
                    self.reporter.attempt(self.username, password, False)

            except Exception as e:
                if self.verbose:
                    self.reporter.error(f"Error: {e}")

            finally:
                self.password_queue.task_done()

    def run(self):
        """Run the brute-force attack."""
        self.reporter.info(f"Target: {self.target}:{self.port}")
        self.reporter.info(f"Username: {self.username}")
        self.reporter.info(f"Threads: {self.threads}")

        if not self.load_wordlist():
            return

        self.reporter.info(f"Passwords loaded: {self.total_passwords}")
        self.reporter.info("Starting brute-force...\n")

        self.reporter.start()

        # Create progress bar
        self.progress_bar = tqdm(
            total=self.total_passwords,
            desc="Progress",
            unit="pwd",
            ncols=80,
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]"
        )

        threads = []
        for _ in range(self.threads):
            t = threading.Thread(target=self.worker, daemon=True)
            t.start()
            threads.append(t)

        self.password_queue.join()

        self.stop_event.set()
        for t in threads:
            t.join()

        if self.progress_bar:
            self.progress_bar.close()

        self.reporter.summary()
        self.reporter.close()
