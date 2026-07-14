"""Base brute-force module."""

import threading
import queue
import time
from typing import Optional, List
from abc import ABC, abstractmethod
from tqdm import tqdm

from core.reporter import Reporter
from core.state import StateManager


class RateLimiter:
    """Detect and handle rate limiting."""

    def __init__(self, max_failures: int = 10, window: int = 60, pause_time: int = 60):
        """
        Args:
            max_failures: Max failures before triggering rate limit
            window: Time window in seconds to track failures
            pause_time: Seconds to pause when rate limited
        """
        self.max_failures = max_failures
        self.window = window
        self.pause_time = pause_time
        self.failures = []
        self.lock = threading.Lock()
        self.is_paused = False
        self.total_pauses = 0

    def record_failure(self):
        """Record a failure timestamp."""
        with self.lock:
            now = time.time()
            self.failures.append(now)
            # Remove old failures outside the window
            self.failures = [f for f in self.failures if now - f < self.window]

    def is_rate_limited(self) -> bool:
        """Check if we should pause due to rate limiting."""
        with self.lock:
            now = time.time()
            # Count failures in current window
            recent_failures = [f for f in self.failures if now - f < self.window]
            return len(recent_failures) >= self.max_failures

    def pause(self, reporter=None):
        """Pause execution due to rate limiting."""
        with self.lock:
            if self.is_paused:
                return
            self.is_paused = True
            self.total_pauses += 1

        if reporter:
            reporter.warning(f"Rate limit detected! ({self.max_failures} failures in {self.window}s)")
            reporter.warning(f"Pausing for {self.pause_time} seconds...")

        time.sleep(self.pause_time)

        with self.lock:
            self.is_paused = False
            # Clear old failures after pause
            self.failures = []

        if reporter:
            reporter.info("Resuming brute-force...")


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
        delay: float = 0.0,
        proxy: Optional[str] = None,
        rate_limit: bool = False,
        rate_max_failures: int = 10,
        rate_window: int = 60,
        rate_pause_time: int = 60,
    ):
        self.target = target
        self.port = port
        self.username = username
        self.wordlist = wordlist
        self.threads = threads
        self.output_file = output_file
        self.verbose = verbose
        self.delay = delay
        self.proxy = proxy

        self.password_queue = queue.Queue()
        self.found = []
        self.attempts = 0
        self.total_passwords = 0
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self.reporter = Reporter(verbose=verbose, output_file=output_file)
        self.state_manager = StateManager()
        self.progress_bar = None

        # Rate limiter
        self.rate_limit_enabled = rate_limit
        if rate_limit:
            self.rate_limiter = RateLimiter(
                max_failures=rate_max_failures,
                window=rate_window,
                pause_time=rate_pause_time,
            )
        else:
            self.rate_limiter = None

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
                # Check rate limit before each attempt
                if self.rate_limiter and self.rate_limiter.is_rate_limited():
                    self.rate_limiter.pause(self.reporter)

                # Apply delay if configured
                if self.delay > 0:
                    time.sleep(self.delay)

                success = self.try_login(self.username, password)

                with self.lock:
                    self.attempts += 1
                    if self.progress_bar:
                        self.progress_bar.update(1)

                if success:
                    with self.lock:
                        self.found.append((self.username, password))
                    self.reporter.attempt(self.username, password, True)
                else:
                    # Record failure for rate limiting
                    if self.rate_limiter:
                        self.rate_limiter.record_failure()
                    if self.verbose:
                        self.reporter.attempt(self.username, password, False)

            except Exception as e:
                if self.verbose:
                    self.reporter.error(f"Error: {e}")

            finally:
                self.password_queue.task_done()

    def save_state(self):
        """Save current attack state."""
        self.state_manager.save_attack_state(
            target=self.target,
            port=self.port,
            username=self.username,
            wordlist=self.wordlist,
            attempts=self.attempts,
            found=self.found,
        )

    def run(self, resume: bool = False):
        """Run the brute-force attack."""
        self.reporter.info(f"Target: {self.target}:{self.port}")
        self.reporter.info(f"Username: {self.username}")
        self.reporter.info(f"Threads: {self.threads}")
        if self.delay > 0:
            self.reporter.info(f"Delay: {self.delay}s between attempts")
        if self.proxy:
            self.reporter.info(f"Proxy: {self.proxy}")
        if self.rate_limit_enabled:
            self.reporter.info(f"Rate limit: enabled (pause after {self.rate_limiter.max_failures} failures)")

        # Check for saved state
        if resume:
            saved = self.state_manager.get_attack_state(
                self.target, self.port, self.username
            )
            if saved:
                self.reporter.info(f"Resuming from attempt {saved['attempts']}")
                self.attempts = saved.get("attempts", 0)
                self.found = saved.get("found", [])

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

        # Save final state
        self.save_state()

        # Print rate limit stats
        if self.rate_limiter and self.rate_limiter.total_pauses > 0:
            self.reporter.warning(f"Rate limit triggered {self.rate_limiter.total_pauses} times")

        self.reporter.summary()
        self.reporter.close()


class MultiUserBrute:
    """Run brute-force for multiple usernames."""

    def __init__(self, brute_class, target: str, port: int, usernames: List[str],
                 wordlist: str, threads: int = 5, output_file: Optional[str] = None,
                 verbose: bool = False, delay: float = 0.0, proxy: Optional[str] = None,
                 rate_limit: bool = False, rate_max_failures: int = 10,
                 rate_window: int = 60, rate_pause_time: int = 60,
                 **kwargs):
        self.brute_class = brute_class
        self.target = target
        self.port = port
        self.usernames = usernames
        self.wordlist = wordlist
        self.threads = threads
        self.output_file = output_file
        self.verbose = verbose
        self.delay = delay
        self.proxy = proxy
        self.rate_limit = rate_limit
        self.rate_max_failures = rate_max_failures
        self.rate_window = rate_window
        self.rate_pause_time = rate_pause_time
        self.kwargs = kwargs
        self.all_found = []

    def run(self, resume: bool = False):
        """Run brute-force for all usernames."""
        print(f"[*] Running brute-force for {len(self.usernames)} usernames\n")

        for i, username in enumerate(self.usernames, 1):
            print(f"[*] [{i}/{len(self.usernames)}] Testing username: {username}")

            module = self.brute_class(
                target=self.target,
                port=self.port,
                username=username,
                wordlist=self.wordlist,
                threads=self.threads,
                output_file=self.output_file,
                verbose=self.verbose,
                delay=self.delay,
                proxy=self.proxy,
                rate_limit=self.rate_limit,
                rate_max_failures=self.rate_max_failures,
                rate_window=self.rate_window,
                rate_pause_time=self.rate_pause_time,
                **self.kwargs,
            )
            module.run(resume=resume)

            if module.found:
                self.all_found.extend(module.found)

        print(f"\n{'='*50}")
        print(f"[*] TOTAL FOUND: {len(self.all_found)} credentials")
        for user, pwd in self.all_found:
            print(f"    {user}:{pwd}")
        print(f"{'='*50}")
