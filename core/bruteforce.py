"""Base brute-force module."""

import threading
import queue
import time
from typing import Optional, Callable
from abc import ABC, abstractmethod


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
        self.start_time = None
        self.lock = threading.Lock()
        self.stop_event = threading.Event()

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
            return True
        except FileNotFoundError:
            print(f"[!] Wordlist not found: {self.wordlist}")
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

                if success:
                    with self.lock:
                        self.found.append((self.username, password))
                    print(f"\n[+] FOUND: {self.username}:{password}")
                    self._save_result(self.username, password)
                elif self.verbose:
                    print(f"[-] Failed: {self.username}:{password}")

            except Exception as e:
                if self.verbose:
                    print(f"[!] Error: {e}")

            finally:
                self.password_queue.task_done()

    def _save_result(self, username: str, password: str):
        """Save found credentials to file."""
        if self.output_file:
            with open(self.output_file, "a") as f:
                f.write(f"{username}:{password}\n")
        else:
            with open("output/Found.txt", "a") as f:
                f.write(f"{username}:{password}\n")

    def run(self):
        """Run the brute-force attack."""
        print(f"[*] Target: {self.target}:{self.port}")
        print(f"[*] Username: {self.username}")
        print(f"[*] Threads: {self.threads}")

        if not self.load_wordlist():
            return

        total = self.password_queue.qsize()
        print(f"[*] Passwords loaded: {total}")
        print("[*] Starting brute-force...\n")

        self.start_time = time.time()

        threads = []
        for _ in range(self.threads):
            t = threading.Thread(target=self.worker, daemon=True)
            t.start()
            threads.append(t)

        self.password_queue.join()

        self.stop_event.set()
        for t in threads:
            t.join()

        elapsed = time.time() - self.start_time
        print(f"\n[*] Completed in {elapsed:.2f}s")
        print(f"[*] Attempts: {self.attempts}")

        if self.found:
            print(f"\n[+] Found {len(self.found)} valid credential(s):")
            for user, pwd in self.found:
                print(f"    {user}:{pwd}")
        else:
            print("[-] No valid credentials found.")
