"""State manager for resume capability."""

import os
import json
import time
from typing import Optional


class StateManager:
    """Manages attack state for resume capability."""

    def __init__(self, state_file: str = "output/.state.json"):
        self.state_file = state_file
        self.state = self._load()

    def _load(self) -> dict:
        """Load state from file."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def save(self, data: dict):
        """Save state to file."""
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        with open(self.state_file, "w") as f:
            json.dump(data, f, indent=2)

    def save_attack_state(self, target: str, port: int, username: str,
                          wordlist: str, attempts: int, found: list):
        """Save attack progress."""
        key = f"{target}:{port}:{username}"
        self.state[key] = {
            "target": target,
            "port": port,
            "username": username,
            "wordlist": wordlist,
            "attempts": attempts,
            "found": found,
            "timestamp": time.time(),
            "last_update": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        self.save(self.state)

    def get_attack_state(self, target: str, port: int, username: str) -> Optional[dict]:
        """Get saved attack state."""
        key = f"{target}:{port}:{username}"
        return self.state.get(key)

    def clear_attack_state(self, target: str, port: int, username: str):
        """Clear saved attack state."""
        key = f"{target}:{port}:{username}"
        if key in self.state:
            del self.state[key]
            self.save(self.state)

    def list_saved_states(self) -> list:
        """List all saved attack states."""
        states = []
        for key, value in self.state.items():
            states.append({
                "key": key,
                "target": value.get("target"),
                "port": value.get("port"),
                "username": value.get("username"),
                "attempts": value.get("attempts", 0),
                "timestamp": value.get("last_update"),
            })
        return states
