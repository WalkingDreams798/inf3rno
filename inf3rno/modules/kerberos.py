"""Kerberos brute-force module."""

import socket
import struct
from core.bruteforce import BaseBrute


class KerberosBrute(BaseBrute):
    """Kerberos brute-force implementation (AS-REQ)."""

    def __init__(self, target: str, port: int = 88, username: str = "administrator",
                 wordlist: str = "wordlists/passwords.txt", threads: int = 5,
                 output_file: str = None, verbose: bool = False,
                 delay: float = 0.0, proxy: str = None,
                 domain: str = None):
        super().__init__(target, port, username, wordlist, threads, output_file, verbose, delay, proxy)
        self.service = "Kerberos"
        self.domain = domain

    def try_login(self, username: str, password: str) -> bool:
        """Attempt Kerberos AS-REQ authentication."""
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((self.target, self.port))

            # Build AS-REQ packet
            as_req = self._build_as_req(username, password)
            sock.send(as_req)

            # Receive response
            response = sock.recv(4096)

            if not response:
                return False

            # Parse response
            # KRB_ERROR = 30 (0x1e) - authentication failed
            # KRB_AS_REP = 11 (0x0b) - authentication successful
            if len(response) >= 1:
                msg_type = response[0]

                # Check for KRB_ERROR (might contain error code)
                if msg_type == 0x1e:  # KRB_ERROR
                    # Parse error code
                    error_code = self._parse_error_code(response)
                    if error_code == 23:  # KDC_ERR_WRONG_REALM
                        return False
                    elif error_code == 14:  # KDC_ERR_C_PRINCIPAL_UNKNOWN
                        return False
                    elif error_code == 18:  # KDC_ERR_PREAUTH_FAILED
                        # Pre-auth failed might mean user exists
                        return False
                    elif error_code == 0:  # No error
                        return True
                    return False

                elif msg_type == 0x0b:  # KRB_AS_REP
                    return True

            return False

        except socket.timeout:
            if self.verbose:
                print(f"[!] Kerberos timeout for {username}:{password}")
            return False
        except ConnectionRefusedError:
            if self.verbose:
                print(f"[!] Kerberos connection refused")
            return False
        except Exception as e:
            if self.verbose:
                print(f"[!] Kerberos error for {username}:{password}: {e}")
            return False
        finally:
            if sock:
                try:
                    sock.close()
                except Exception:
                    pass

    def _build_as_req(self, username: str, password: str):
        """Build Kerberos AS-REQ packet."""
        # Simplified AS-REQ structure
        # In production, use proper ASN.1/DER encoding

        realm = self.domain.upper() if self.domain else "DOMAIN"

        # ASN.1 structure (simplified)
        # SEQUENCE {
        #   SEQUENCE { pvno, msg-type }
        #   SEQUENCE { padata-type, padata-value }
        #   SEQUENCE { KDC-REQ-BODY }
        # }

        # For now, send a minimal AS-REQ
        # Real implementation would use proper Kerberos library
        return b'\x00' * 32  # Placeholder

    def _parse_error_code(self, response: bytes) -> int:
        """Parse error code from KRB_ERROR response."""
        try:
            # Simplified error code extraction
            # Look for error code in response
            if len(response) >= 10:
                # Check for common error patterns
                for i in range(len(response) - 2):
                    if response[i] == 0x30:  # SEQUENCE tag
                        # Try to extract error code
                        error_code = response[i + 5] if i + 5 < len(response) else -1
                        return error_code
            return -1
        except Exception:
            return -1

    def get_userrealm(self, username: str) -> str:
        """Get realm from username (domain\\user format)."""
        if "\\" in username:
            return username.split("\\")[0].upper()
        return self.domain.upper() if self.domain else "DOMAIN"


class KerberosUserEnum:
    """Kerberos username enumeration."""

    def __init__(self, target: str, port: int = 88, domain: str = None):
        self.target = target
        self.port = port
        self.domain = domain

    def check_user(self, username: str) -> dict:
        """
        Check if username exists in Kerberos.

        Returns:
            Dictionary with user status
        """
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((self.target, self.port))

            # Build AS-REQ with invalid password
            as_req = self._build_as_req(username, "invalid_password_test")
            sock.send(as_req)

            response = sock.recv(4096)

            if not response:
                return {"username": username, "exists": False, "error": "No response"}

            # Parse response
            error_code = self._parse_error_code(response)

            # KDC_ERR_C_PRINCIPAL_UNKNOWN (7) = user doesn't exist
            # KDC_ERR_PREAUTH_REQUIRED (25) = user exists but needs pre-auth
            # KDC_ERR_PREAUTH_FAILED (18) = user exists but wrong password
            if error_code == 7:
                return {"username": username, "exists": False, "error": "User not found"}
            elif error_code in [18, 25]:
                return {"username": username, "exists": True, "error": None}
            else:
                return {"username": username, "exists": None, "error": f"Error code: {error_code}"}

        except socket.timeout:
            return {"username": username, "exists": None, "error": "Timeout"}
        except ConnectionRefusedError:
            return {"username": username, "exists": None, "error": "Connection refused"}
        except Exception as e:
            return {"username": username, "exists": None, "error": str(e)}
        finally:
            if sock:
                try:
                    sock.close()
                except Exception:
                    pass

    def _build_as_req(self, username: str, password: str):
        """Build AS-REQ packet."""
        return b'\x00' * 32  # Placeholder

    def _parse_error_code(self, response: bytes) -> int:
        """Parse error code from response."""
        try:
            if len(response) >= 10:
                for i in range(len(response) - 2):
                    if response[i] == 0x30:
                        error_code = response[i + 5] if i + 5 < len(response) else -1
                        return error_code
            return -1
        except Exception:
            return -1
