"""Password generator module."""

import itertools
import os
import random
import string
from typing import List


class PasswordGenerator:
    """Generate passwords based on mask or rules."""

    CHARSETS = {
        "l": string.ascii_lowercase,
        "u": string.ascii_uppercase,
        "d": string.digits,
        "s": string.punctuation,
        "?": "?",
    }

    LEET_MAP = {
        "a": "4", "e": "3", "i": "1", "o": "0", "s": "5",
        "t": "7", "A": "4", "E": "3", "I": "1", "O": "0",
        "S": "5", "T": "7",
    }

    def __init__(self):
        self.generated = set()

    def generate_mask(self, mask: str, max_length: int = 8):
        """
        Generate passwords based on mask pattern.

        Mask characters:
            ?l = lowercase
            ?u = uppercase
            ?d = digits
            ?s = special characters
            ?a = all characters
            ?? = literal question mark
        """
        charset_list = []
        i = 0
        while i < len(mask):
            if mask[i] == "?" and i + 1 < len(mask):
                next_char = mask[i + 1]
                if next_char == "a":
                    charset_list.append(string.ascii_letters + string.digits + string.punctuation)
                elif next_char in self.CHARSETS:
                    charset_list.append(self.CHARSETS[next_char])
                else:
                    charset_list.append(next_char)
                i += 2
            else:
                charset_list.append(mask[i])
                i += 1

        for combo in itertools.product(*charset_list):
            password = "".join(combo)
            if password not in self.generated:
                self.generated.add(password)
                yield password

    def generate_length(self, length: int, charset: str = "all"):
        """Generate all passwords of given length."""
        if charset == "all":
            chars = string.ascii_letters + string.digits + string.punctuation
        elif charset == "alpha":
            chars = string.ascii_letters
        elif charset == "digits":
            chars = string.digits
        elif charset == "alphanum":
            chars = string.ascii_letters + string.digits
        else:
            chars = charset

        for combo in itertools.product(chars, repeat=length):
            password = "".join(combo)
            if password not in self.generated:
                self.generated.add(password)
                yield password

    def generate_random(self, count: int, min_len: int = 6, max_len: int = 12,
                        use_upper: bool = True, use_digits: bool = True,
                        use_special: bool = True):
        """Generate random passwords."""
        chars = string.ascii_lowercase
        if use_upper:
            chars += string.ascii_uppercase
        if use_digits:
            chars += string.digits
        if use_special:
            chars += string.punctuation

        for _ in range(count):
            length = random.randint(min_len, max_len)
            password = "".join(random.choices(chars, k=length))
            if password not in self.generated:
                self.generated.add(password)
                yield password

    def apply_rules(self, word: str, rules: List[str] = None) -> List[str]:
        """Apply rules to a word and return all variations."""
        if rules is None:
            rules = ["leet", "capitalize", "append_number", "prepend_number",
                     "duplicate", "reverse"]

        variations = [word]

        for rule in rules:
            new_variations = []
            for variation in variations:
                new_variations.extend(self._apply_rule(variation, rule))
            variations.extend(new_variations)

        # Deduplicate
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
            leet_word = ""
            for char in word:
                leet_word += self.LEET_MAP.get(char, char)
            if leet_word != word:
                results.append(leet_word)
            # Partial leet (only some chars)
            for char, replacement in self.LEET_MAP.items():
                if char in word or char.upper() in word:
                    partial = word.replace(char, replacement)
                    partial = partial.replace(char.upper(), replacement)
                    if partial != word:
                        results.append(partial)

        elif rule == "capitalize":
            if word.islower():
                results.append(word.capitalize())
            if word.isupper():
                results.append(word.lower())
            if not word[0].isupper():
                results.append(word[0].upper() + word[1:])

        elif rule == "append_number":
            for i in range(10):
                results.append(f"{word}{i}")
            results.append(f"{word}123")
            results.append(f"{word}1234")
            results.append(f"{word}!")
            results.append(f"{word}@")
            results.append(f"{word}#")

        elif rule == "prepend_number":
            for i in range(10):
                results.append(f"{i}{word}")
            results.append(f"123{word}")
            results.append(f"1234{word}")

        elif rule == "duplicate":
            results.append(word * 2)

        elif rule == "reverse":
            results.append(word[::-1])

        elif rule == "uppercase":
            results.append(word.upper())

        elif rule == "lowercase":
            results.append(word.lower())

        elif rule == "swapcase":
            results.append(word.swapcase())

        return results

    def generate_from_words(self, words: List[str], rules: List[str] = None) -> List[str]:
        """Generate password variations from a list of words."""
        all_passwords = []

        for word in words:
            variations = self.apply_rules(word, rules)
            all_passwords.extend(variations)

        # Deduplicate while preserving order
        seen = set()
        unique = []
        for p in all_passwords:
            if p not in seen:
                seen.add(p)
                unique.append(p)

        return unique

    def save_to_file(self, filename: str, passwords):
        """Save generated passwords to file."""
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else ".", exist_ok=True)
        with open(filename, "w") as f:
            if hasattr(passwords, '__iter__') and not isinstance(passwords, (str, bytes)):
                count = 0
                for password in passwords:
                    f.write(f"{password}\n")
                    count += 1
                print(f"[*] Generated {count} passwords -> {filename}")
            else:
                f.write(f"{passwords}\n")
                print(f"[*] Generated 1 password -> {filename}")
