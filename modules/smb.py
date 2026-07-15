"""SMB brute-force module."""

import socket
import struct
from core.bruteforce import BaseBrute


class SMBBrute(BaseBrute):
    """SMB brute-force implementation."""

    def __init__(self, target: str, port: int = 445, username: str = "Administrator",
                 wordlist: str = "wordlists/passwords.txt", threads: int = 5,
                 output_file: str = None, verbose: bool = False,
                 delay: float = 0.0, proxy: str = None):
        super().__init__(target, port, username, wordlist, threads, output_file, verbose, delay, proxy)
        self.service = "SMB"

    def try_login(self, username: str, password: str) -> bool:
        """Attempt SMB login using NTLM authentication."""
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((self.target, self.port))

            # SMB Negotiate Protocol Request
            negotiate_request = self._build_negotiate_request()
            sock.send(negotiate_request)

            # Receive response
            response = sock.recv(4096)

            if not response:
                return False

            # Check for SMB signature
            if len(response) < 8:
                return False

            # Send Session Setup Request with NTLM
            session_setup = self._build_session_setup(username, password)
            sock.send(session_setup)

            # Receive response
            response = sock.recv(4096)

            if not response:
                return False

            # Parse response
            # NTLM response contains status code
            if len(response) >= 36:
                # STATUS_SUCCESS = 0x00000000
                # STATUS_LOGON_FAILURE = 0xC000006D
                status_code = struct.unpack('<I', response[32:36])[0]

                if status_code == 0x00000000:
                    return True
                elif status_code == 0xC000006D:
                    return False
                elif status_code == 0xC000006A:
                    # STATUS_NO_SUCH_USER
                    return False
                elif status_code == 0xC0000022:
                    # STATUS_ACCESS_DENIED - user exists but wrong password
                    return False

            return False

        except socket.timeout:
            if self.verbose:
                print(f"[!] SMB timeout for {username}:{password}")
            return False
        except ConnectionRefusedError:
            if self.verbose:
                print(f"[!] SMB connection refused")
            return False
        except Exception as e:
            if self.verbose:
                print(f"[!] SMB error for {username}:{password}: {e}")
            return False
        finally:
            if sock:
                try:
                    sock.close()
                except Exception:
                    pass

    def _build_negotiate_request(self):
        """Build SMB Negotiate Protocol Request."""
        # SMB Header
        smb_header = b'\xffSMB'  # Protocol
        smb_header += b'\x00' * 4  # Status
        smb_header += b'\x18'  # Flags
        smb_header += b'\xc7'  # Flags2
        smb_header += b'\x00' * 2  # PID High
        smb_header += b'\x00' * 8  # Signature
        smb_header += b'\x00' * 2  # Reserved
        smb_header += b'\x3c\x00'  # TID
        smb_header += b'\x00\x00'  # PID
        smb_header += b'\x00\x00'  # UID
        smb_header += b'\x00\x00'  # MID

        # Negotiate Protocol Request
        word_count = b'\x00'  # Word Count
        byte_count = b'\x22\x00'  # Byte Count
        dialects = b'\x02NT LM 0.12\x00'

        return b'\x00' * 4 + smb_header + word_count + byte_count + dialects

    def _build_session_setup(self, username, password):
        """Build Session Setup Request with NTLM authentication."""
        # Simplified NTLM authentication
        # In real implementation, you'd need proper NTLM hash computation

        smb_header = b'\xffSMB'
        smb_header += b'\x00' * 4  # Status
        smb_header += b'\x18'  # Flags
        smb_header += b'\xc7'  # Flags2
        smb_header += b'\x00' * 2  # PID High
        smb_header += b'\x00' * 8  # Signature
        smb_header += b'\x00' * 2  # Reserved
        smb_header += b'\x3c\x00'  # TID
        smb_header += b'\x00\x00'  # PID
        smb_header += b'\x00\x00'  # UID
        smb_header += b'\x00\x00'  # MID

        # Session Setup Request
        word_count = b'\x0c'  # Word Count
        andx = b'\xff\x00'  # AndX
        max_buff = b'\x00\x04'  # Max Buffer Size
        max_mpx = b'\x02\x00'  # Max Multiplex
        vc_num = b'\x01\x00'  # VC Number
        session_key = b'\x00\x00\x00\x00'  # Session Key
        security_blob_len = b'\x00\x00'  # Security Blob Length (simplified)

        # Build security blob (simplified)
        # In real implementation, use proper NTLM
        ntlm_auth = self._build_ntlm_auth(username, password)

        return smb_header + word_count + andx + max_buff + max_mpx + vc_num + session_key + security_blob_len + ntlm_auth

    def _build_ntlm_auth(self, username, password):
        """Build NTLM authentication blob."""
        # Simplified - in production, use proper NTLMv2
        # This is a placeholder for the structure
        return b'\x00' * 16
