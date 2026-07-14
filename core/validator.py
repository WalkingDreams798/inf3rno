"""Credential validator module."""

import os
import json
from datetime import datetime
from typing import List, Tuple, Optional


class CredentialValidator:
    """Validate found credentials and manage results."""

    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def validate_credential(self, username: str, password: str,
                            service: str = "", target: str = "") -> dict:
        """Validate and format a credential entry."""
        return {
            "username": username,
            "password": password,
            "service": service,
            "target": target,
            "timestamp": datetime.now().isoformat(),
            "validated": True,
        }

    def load_found_credentials(self, filename: str = "Found.txt") -> List[dict]:
        """Load found credentials from file."""
        filepath = os.path.join(self.output_dir, filename)
        credentials = []

        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                for line in f:
                    line = line.strip()
                    if ":" in line:
                        username, password = line.split(":", 1)
                        credentials.append({
                            "username": username,
                            "password": password,
                            "validated": False,
                        })

        return credentials

    def save_validated_credentials(self, credentials: List[dict],
                                   filename: str = "Validated.json"):
        """Save validated credentials to JSON file."""
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, "w") as f:
            json.dump(credentials, f, indent=2)

        print(f"[*] Saved {len(credentials)} validated credentials -> {filepath}")
        return filepath

    def check_duplicate(self, username: str, password: str,
                        credentials: List[dict]) -> bool:
        """Check if credential already exists."""
        for cred in credentials:
            if cred["username"] == username and cred["password"] == password:
                return True
        return False

    def merge_credentials(self, *credential_lists) -> List[dict]:
        """Merge multiple credential lists and remove duplicates."""
        merged = []
        seen = set()

        for cred_list in credential_lists:
            for cred in cred_list:
                key = (cred["username"], cred["password"])
                if key not in seen:
                    seen.add(key)
                    merged.append(cred)

        return merged

    def export_credential_report(self, credentials: List[dict],
                                 target: str = "", service: str = "") -> str:
        """Export credential report to JSON."""
        report = {
            "tool": "Inf3rno",
            "timestamp": datetime.now().isoformat(),
            "target": target,
            "service": service,
            "total_credentials": len(credentials),
            "credentials": credentials,
        }

        filename = f"credential_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, "w") as f:
            json.dump(report, f, indent=2)

        print(f"[*] Credential report saved -> {filepath}")
        return filepath

    def print_summary(self, credentials: List[dict]):
        """Print summary of credentials."""
        print(f"\n{'='*60}")
        print(f"[*] CREDENTIAL SUMMARY")
        print(f"{'='*60}")
        print(f"Total credentials found: {len(credentials)}")
        print(f"\nCredentials:")
        for i, cred in enumerate(credentials, 1):
            validated = "✓" if cred.get("validated") else "?"
            print(f"  {i}. [{validated}] {cred['username']}:{cred['password']}")
        print(f"{'='*60}\n")
