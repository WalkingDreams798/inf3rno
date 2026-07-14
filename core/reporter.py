"""Reporter module for colored output and logging."""

import os
import time
from datetime import datetime
from typing import Optional

from colorama import Fore, Style, init

init(autoreset=True)


class Colors:
    """Color constants."""
    RED = Fore.RED
    GREEN = Fore.GREEN
    YELLOW = Fore.YELLOW
    BLUE = Fore.BLUE
    CYAN = Fore.CYAN
    WHITE = Fore.WHITE
    RESET = Style.RESET_ALL
    BRIGHT = Style.BRIGHT


class Reporter:
    """Handles output formatting and logging."""

    def __init__(self, verbose: bool = False, output_file: Optional[str] = None):
        self.verbose = verbose
        self.output_file = output_file
        self.start_time = None
        self.attempts = 0
        self.found = []
        self.log_file = None

        if output_file:
            log_dir = os.path.dirname(output_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
            log_path = output_file.replace(".txt", "_log.txt")
            self.log_file = open(log_path, "w")

    def start(self):
        """Start the timer."""
        self.start_time = time.time()

    def info(self, message: str):
        """Print info message."""
        print(f"{Colors.CYAN}[*]{Colors.RESET} {message}")

    def success(self, message: str):
        """Print success message."""
        print(f"{Colors.GREEN}[+]{Colors.RESET} {message}")

    def error(self, message: str):
        """Print error message."""
        print(f"{Colors.RED}[-]{Colors.RESET} {message}")

    def warning(self, message: str):
        """Print warning message."""
        print(f"{Colors.YELLOW}[!]{Colors.RESET} {message}")

    def attempt(self, username: str, password: str, success: bool):
        """Log an attempt."""
        self.attempts += 1

        if success:
            self.found.append((username, password))
            self.success(f"FOUND: {username}:{password}")
            self._save_credential(username, password)
        elif self.verbose:
            self.error(f"Failed: {username}:{password}")

        if self.log_file:
            status = "SUCCESS" if success else "FAILED"
            self.log_file.write(
                f"[{datetime.now().isoformat()}] {status}: {username}:{password}\n"
            )

    def _save_credential(self, username: str, password: str):
        """Save found credential to file."""
        if self.output_file:
            with open(self.output_file, "a") as f:
                f.write(f"{username}:{password}\n")
        else:
            os.makedirs("output", exist_ok=True)
            with open("output/Found.txt", "a") as f:
                f.write(f"{username}:{password}\n")

    def summary(self):
        """Print final summary."""
        elapsed = time.time() - self.start_time if self.start_time else 0

        print(f"\n{Colors.CYAN}{'='*50}{Colors.RESET}")
        print(f"{Colors.CYAN}[*] SUMMARY{Colors.RESET}")
        print(f"{Colors.CYAN}{'='*50}{Colors.RESET}")
        print(f"{Colors.WHITE}Time elapsed:{Colors.RESET} {elapsed:.2f}s")
        print(f"{Colors.WHITE}Attempts:{Colors.RESET} {self.attempts}")

        if self.found:
            print(f"\n{Colors.GREEN}[+] Found {len(self.found)} valid credential(s):{Colors.RESET}")
            for user, pwd in self.found:
                print(f"    {Colors.GREEN}{user}:{pwd}{Colors.RESET}")
        else:
            print(f"\n{Colors.RED}[-] No valid credentials found.{Colors.RESET}")

        print(f"{Colors.CYAN}{'='*50}{Colors.RESET}\n")

    def close(self):
        """Close log file."""
        if self.log_file:
            self.log_file.close()
