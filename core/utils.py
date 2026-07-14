"""Utility functions."""

import socket
import sys
from typing import Optional, Tuple


def check_port(target: str, port: int, timeout: float = 2.0) -> bool:
    """Check if a port is open."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex((target, port))
            return result == 0
    except socket.error:
        return False


def resolve_target(target: str) -> Optional[str]:
    """Resolve hostname to IP address."""
    try:
        ip = socket.gethostbyname(target)
        return ip
    except socket.gaierror:
        return None


def detect_service(target: str, port: int) -> Optional[str]:
    """Detect service running on a port."""
    services = {
        21: "FTP",
        22: "SSH",
        23: "Telnet",
        25: "SMTP",
        80: "HTTP",
        110: "POP3",
        143: "IMAP",
        443: "HTTPS",
        993: "IMAPS",
        995: "POP3S",
        3306: "MySQL",
        3389: "RDP",
        5432: "PostgreSQL",
        6379: "Redis",
        8080: "HTTP-Proxy",
        8443: "HTTPS-Alt",
    }

    if port in services:
        return services[port]

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(2)
            sock.connect((target, port))
            banner = sock.recv(1024).decode("utf-8", errors="ignore").strip()

            if "SSH" in banner:
                return "SSH"
            elif "FTP" in banner:
                return "FTP"
            elif "HTTP" in banner:
                return "HTTP"
            elif "SMTP" in banner:
                return "SMTP"
            else:
                return "Unknown"

    except socket.error:
        return None


def scan_common_ports(target: str, ports: list = None) -> list:
    """Scan common ports and return open ones."""
    if ports is None:
        ports = [21, 22, 23, 25, 80, 443, 445, 3389, 3306, 8080, 8443]

    open_ports = []
    for port in ports:
        if check_port(target, port):
            service = detect_service(target, port)
            open_ports.append((port, service))
    return open_ports


def print_banner():
    """Print the Inf3rno banner."""
    banner = r"""
    _____ _____ ____  __  __ ____  _     ___ _____ ____
   |_   _| ____|  _ \|  \/  |  _ \| |   |_ _|_   _/ ___|
     | | |  _| | |_) | |\/| | |_) | |    | |  | | \___ \
     | | | |___|  _ <| |  | |  __/| |___ | |  | |  ___) |
     |_| |_____|_| \_\_|  |_|_|   |_____|___| |_| |____/
    """
    print(banner)
    print("    [ Multi-Protocol Brute-Force Tool ]")
    print("    [ by WalkingDreams798              ]")
    print()
