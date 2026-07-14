"""Password generator module."""

import itertools
import random
import string


class PasswordGenerator:
    """Generate passwords based on mask or rules."""

    CHARSETS = {
        "l": string.ascii_lowercase,
        "u": string.ascii_uppercase,
        "d": string.digits,
        "s": string.punctuation,
        "?": "?",
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

        Example: ?l?l?l?d?d generates "abc12", "xyz99", etc.
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

    def save_to_file(self, filename: str, passwords):
        """Save generated passwords to file."""
        with open(filename, "w") as f:
            for password in passwords:
                f.write(f"{password}\n")
        print(f"[*] Generated {len(self.generated)} passwords -> {filename}")
