"""SNMP brute-force module."""

import socket
import struct
from inf3rno.core.bruteforce import BaseBrute


class SNMPBrute(BaseBrute):
    """SNMP brute-force implementation (community string)."""

    def __init__(self, target: str, port: int = 161, username: str = "",
                 wordlist: str = "wordlists/passwords.txt", threads: int = 5,
                 output_file: str = None, verbose: bool = False,
                 delay: float = 0.0, proxy: str = None):
        # SNMP doesn't use username, only community string
        super().__init__(target, port, "community", wordlist, threads, output_file, verbose, delay, proxy)
        self.service = "SNMP"

    def try_login(self, username: str, community: str) -> bool:
        """Test SNMP community string."""
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(3)

            # Build SNMP GET request for sysDescr (.1.3.6.1.2.1.1.1.0)
            request = self._build_snmp_request(community, "get", "1.3.6.1.2.1.1.1.0")

            # Send request
            sock.sendto(request, (self.target, self.port))

            # Receive response
            data, addr = sock.recvfrom(1024)

            if not data:
                return False

            # Check if response is valid SNMP response
            if self._is_valid_snmp_response(data):
                return True

            return False

        except socket.timeout:
            # Timeout might mean community string is valid but host is slow
            return False
        except ConnectionRefusedError:
            if self.verbose:
                print(f"[!] SNMP connection refused")
            return False
        except Exception as e:
            if self.verbose:
                print(f"[!] SNMP error for community '{community}': {e}")
            return False
        finally:
            if sock:
                try:
                    sock.close()
                except Exception:
                    pass

    def _build_snmp_request(self, community, method, oid):
        """Build SNMP request packet."""
        # SNMP version 2c
        version = b'\x02\x01\x01'  # Version 2c

        # Community string
        community_bytes = community.encode('utf-8')
        community_len = len(community_bytes)
        if community_len < 128:
            community_field = b'\x04' + bytes([community_len]) + community_bytes
        else:
            community_field = b'\x04\x81' + bytes([community_len]) + community_bytes

        # Parse OID
        oid_parts = [int(x) for x in oid.split('.')]
        oid_bytes = self._encode_oid(oid_parts)

        # PDU type (0 = GetRequest, 1 = GetNextRequest)
        if method == "get":
            pdu_type = b'\xa0'
        else:
            pdu_type = b'\xa1'

        # Build PDU
        request_id = b'\x00\x00\x00\x01'  # Request ID
        error_status = b'\x02\x01\x00'  # Error status
        error_index = b'\x02\x01\x00'  # Error index
        varbind = b'\x30' + bytes([len(oid_bytes)]) + oid_bytes + b'\x05\x00'  # VarBind (NULL)

        pdu_content = request_id + error_status + error_index + varbind
        pdu = pdu_type + bytes([len(pdu_content)]) + pdu_content

        # Build complete packet
        content = version + community_field + pdu
        packet = b'\x30' + bytes([len(content)]) + content

        return packet

    def _encode_oid(self, oid_parts):
        """Encode OID to SNMP format."""
        if len(oid_parts) < 2:
            return b''

        # First two nodes are encoded together
        encoded = bytes([oid_parts[0] * 40 + oid_parts[1]])

        # Encode remaining nodes
        for part in oid_parts[2:]:
            if part < 128:
                encoded += bytes([part])
            else:
                # Variable length encoding
                temp = []
                temp.append(part & 0x7f)
                part >>= 7
                while part:
                    temp.append((part & 0x7f) | 0x80)
                    part >>= 7
                encoded += bytes(reversed(temp))

        return b'\x06' + bytes([len(encoded)]) + encoded

    def _is_valid_snmp_response(self, data):
        """Check if data is a valid SNMP response."""
        if len(data) < 10:
            return False

        # Check for SNMP sequence tag (0x30)
        if data[0] != 0x30:
            return False

        # Check for response PDU types (0xa2 = GetResponse)
        for i in range(len(data)):
            if data[i] in [0xa2, 0xa3]:  # GetResponse, SetResponse
                return True

        return False
