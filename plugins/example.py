"""Example plugin for Inf3rno."""

import sys
import os

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.plugin import BruteForcePlugin
from core.bruteforce import BaseBrute


class ExampleBruteModule(BaseBrute):
    """Example brute-force module."""

    def __init__(self, target, port, username, wordlist, **kwargs):
        super().__init__(target, port, username, wordlist, **kwargs)
        self.service = "Example"

    def try_login(self, username, password):
        """Attempt login."""
        # This is an example - implement actual login logic
        print(f"[*] Trying {username}:{password}")
        return False


class ExamplePlugin(BruteForcePlugin):
    """Example brute-force plugin."""

    @property
    def name(self) -> str:
        return "example"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Example plugin for demonstration"

    @property
    def author(self) -> str:
        return "WalkingDreams798"

    @property
    def service(self) -> str:
        return "Example"

    @property
    def default_port(self) -> int:
        return 9999

    def create_module(self, target, port, username, wordlist, **kwargs):
        """Create example module instance."""
        return ExampleBruteModule(
            target=target,
            port=port,
            username=username,
            wordlist=wordlist,
            **kwargs,
        )

    def on_attack_start(self, target, port, username):
        print(f"[*] Example plugin: Attack started on {target}:{port}")

    def on_attempt(self, username, password, success):
        if success:
            print(f"[+] Example plugin: Found {username}:{password}")

    def on_attack_complete(self, found):
        print(f"[*] Example plugin: Attack complete, found {len(found)} credentials")


# Plugin metadata
PLUGIN_NAME = "example"
PLUGIN_VERSION = "1.0.0"
PLUGIN_DESCRIPTION = "Example plugin for demonstration"
PLUGIN_AUTHOR = "WalkingDreams798"
