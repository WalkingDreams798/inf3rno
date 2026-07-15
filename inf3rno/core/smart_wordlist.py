"""Smart wordlist generator based on target information."""

import os
import random
import string
from datetime import datetime
from typing import List, Optional


class SmartWordlist:
    """Generate wordlists based on target information."""

    def __init__(self):
        self.common_passwords = [
            "password", "123456", "12345678", "qwerty", "abc123",
            "monkey", "1234567", "letmein", "trustno1", "dragon",
            "baseball", "iloveyou", "master", "sunshine", "ashley",
            "bailey", "passw0rd", "shadow", "123123", "654321",
            "superman", "qazwsx", "michael", "football", "password1",
            "password123", "admin", "admin123", "root", "toor",
            "pass", "test", "guest", "master", "changeme",
        ]

        self.common_years = [str(y) for y in range(2020, 2030)]
        self.common_months = ["jan", "feb", "mar", "apr", "may", "jun",
                              "jul", "aug", "sep", "oct", "nov", "dec"]

    def generate_from_target(self, target: str, username: str = "",
                             include_numbers: bool = True,
                             include_symbols: bool = False,
                             max_length: int = 12) -> List[str]:
        """Generate passwords based on target info."""
        words = []

        # Extract parts from target
        target_clean = target.replace(".", "").replace("-", "").replace("_", "")
        target_parts = target.split(".")
        target_parts_clean = [p.replace("-", "").replace("_", "") for p in target_parts]

        # Add target-based passwords
        for part in target_parts_clean:
            if len(part) >= 3:
                words.append(part.lower())
                words.append(part.upper())
                words.append(part.capitalize())

        # Add combinations with common suffixes
        suffixes = ["123", "1", "!", "@", "#", "1234", "2024", "2025", "2026"]
        for part in target_parts_clean[:2]:
            if len(part) >= 3:
                for suffix in suffixes:
                    words.append(f"{part.lower()}{suffix}")
                    words.append(f"{part.capitalize()}{suffix}")

        # Add username-based passwords
        if username:
            username_clean = username.replace(".", "").replace("-", "").replace("_", "")
            words.append(username_clean.lower())
            words.append(username_clean.capitalize())

            for suffix in suffixes:
                words.append(f"{username_clean.lower()}{suffix}")
                words.append(f"{username_clean.capitalize()}{suffix}")

            # Combine username and target
            if target_parts_clean:
                words.append(f"{username_clean.lower()}{target_parts_clean[0].lower()}")
                words.append(f"{target_parts_clean[0].lower()}{username_clean.lower()}")

        # Add common patterns
        words.extend(self.common_passwords)

        # Add date-based passwords
        now = datetime.now()
        year = str(now.year)
        month = f"{now.month:02d}"
        day = f"{now.day:02d}"

        date_patterns = [
            year, month + year, day + month + year,
            month + day, year + month + day,
        ]
        words.extend(date_patterns)

        # Add number patterns if enabled
        if include_numbers:
            for i in range(10):
                words.append(str(i))
                words.append(str(i) * 3)
                words.append(str(i) * 4)

        # Add symbol patterns if enabled
        if include_symbols:
            symbols = ["!", "@", "#", "$", "%", "&", "*"]
            words.extend(symbols)

        # Filter and deduplicate
        seen = set()
        unique_words = []
        for word in words:
            word = word.strip()
            if word and len(word) <= max_length and word not in seen:
                seen.add(word)
                unique_words.append(word)

        return unique_words

    def generate_from_word(self, word: str, rules: List[str] = None) -> List[str]:
        """Generate variations of a word using rules."""
        if rules is None:
            rules = ["leet", "capitalize", "append_number", "duplicate"]

        variations = [word]

        for rule in rules:
            new_variations = []
            for variation in variations:
                new_variations.extend(self._apply_rule(variation, rule))
            variations.extend(new_variations)

        # Deduplicate while preserving order
        seen = set()
        unique = []
        for v in variations:
            if v not in seen:
                seen.add(v)
                unique.append(v)

        return unique

    def _apply_rule(self, word: str, rule: str) -> List[str]:
        """Apply a single rule to a word."""
        results = []

        if rule == "leet":
            leet_map = {"a": "4", "e": "3", "i": "1", "o": "0", "s": "5", "t": "7"}
            leet_word = word
            for char, replacement in leet_map.items():
                leet_word = leet_word.replace(char, replacement)
                leet_word = leet_word.replace(char.upper(), replacement)
            if leet_word != word:
                results.append(leet_word)

        elif rule == "capitalize":
            if word.islower():
                results.append(word.capitalize())
            if word.isupper():
                results.append(word.lower())

        elif rule == "append_number":
            for i in range(10):
                results.append(f"{word}{i}")
            results.append(f"{word}123")
            results.append(f"{word}!")
            results.append(f"{word}@")
            results.append(f"{word}#")

        elif rule == "prepend_number":
            for i in range(10):
                results.append(f"{i}{word}")
            results.append(f"123{word}")

        elif rule == "duplicate":
            results.append(word * 2)

        elif rule == "reverse":
            results.append(word[::-1])

        return results

    def save_to_file(self, filename: str, passwords: List[str]):
        """Save wordlist to file."""
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else ".", exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
            for password in passwords:
                f.write(f"{password}\n")
        print(f"[*] Generated {len(passwords)} passwords -> {filename}")
