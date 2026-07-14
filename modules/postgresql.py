"""PostgreSQL brute-force module."""

import psycopg2
from core.bruteforce import BaseBrute


class PostgreSQLBrute(BaseBrute):
    """PostgreSQL brute-force implementation."""

    def __init__(self, target: str, port: int = 5432, username: str = "postgres",
                 wordlist: str = "wordlists/passwords.txt", threads: int = 5,
                 output_file: str = None, verbose: bool = False,
                 delay: float = 0.0, proxy: str = None):
        super().__init__(target, port, username, wordlist, threads, output_file, verbose, delay, proxy)
        self.service = "PostgreSQL"

    def try_login(self, username: str, password: str) -> bool:
        """Attempt PostgreSQL login."""
        conn = None
        try:
            conn = psycopg2.connect(
                host=self.target,
                port=self.port,
                user=username,
                password=password,
                connect_timeout=5,
            )
            conn.close()
            return True

        except psycopg2.OperationalError as e:
            error_msg = str(e).lower()
            if "authentication failed" in error_msg or "password authentication" in error_msg:
                return False
            if self.verbose:
                print(f"[!] PostgreSQL error for {username}:{password}: {e}")
            return False

        except Exception as e:
            if self.verbose:
                print(f"[!] Connection error: {e}")
            return False

        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass
