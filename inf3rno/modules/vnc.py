"""VNC brute-force module."""

import socket
import struct
from inf3rno.core.bruteforce import BaseBrute


class VNCBrute(BaseBrute):
    """VNC brute-force implementation."""

    def __init__(self, target: str, port: int = 5900, username: str = "",
                 wordlist: str = "wordlists/passwords.txt", threads: int = 5,
                 output_file: str = None, verbose: bool = False,
                 delay: float = 0.0, proxy: str = None):
        super().__init__(target, port, username, wordlist, threads, output_file, verbose, delay, proxy)
        self.service = "VNC"

    def try_login(self, username: str, password: str) -> bool:
        """Attempt VNC login."""
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((self.target, self.port))

            # Receive protocol version
            version = sock.recv(1024)
            if not version or b'RFB ' not in version:
                return False

            # Send protocol version
            sock.send(b'RFB 003.008\n')

            # Receive security types
            security_types = sock.recv(1024)
            if not security_types:
                return False

            # Check if VNC authentication is available
            # Type 2 = VNC Authentication
            if len(security_types) < 2 or security_types[0] != 0x02:
                return False

            # Send VNC Authentication type
            sock.send(b'\x02')

            # Receive challenge (16 bytes)
            challenge = sock.recv(16)
            if len(challenge) != 16:
                return False

            # Encrypt password with challenge using DES
            response = self._vnc_encrypt_password(password, challenge)
            sock.send(response)

            # Receive auth result
            result = sock.recv(4)
            if not result:
                return False

            # Check result
            # 0 = OK, 1 = Failed
            if len(result) >= 4:
                status = struct.unpack('>I', result)[0]
                return status == 0

            return False

        except socket.timeout:
            if self.verbose:
                print(f"[!] VNC timeout for {password}")
            return False
        except ConnectionRefusedError:
            if self.verbose:
                print(f"[!] VNC connection refused")
            return False
        except Exception as e:
            if self.verbose:
                print(f"[!] VNC error for {password}: {e}")
            return False
        finally:
            if sock:
                try:
                    sock.close()
                except Exception:
                    pass

    def _vnc_encrypt_password(self, password, challenge):
        """Encrypt password with VNC challenge using DES."""
        # VNC uses a fixed key permutation table
        # This is a simplified implementation
        # In production, use proper DES implementation

        # Pad or truncate password to 8 bytes
        key = password.encode('utf-8')[:8].ljust(8, b'\x00')

        # Simple XOR for demonstration
        # Real VNC uses DES encryption
        response = bytearray(8)
        for i in range(8):
            response[i] = key[i] ^ challenge[i] if i < len(challenge) else key[i]

        return bytes(response)
