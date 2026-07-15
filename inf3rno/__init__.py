"""Inf3rno - Multi-Protocol Brute-Force Tool."""

__version__ = "2.1.0"
__author__ = "WalkingDreams798"

# Lazy imports - only import when accessed
# This prevents import errors when package isn't fully installed

def __getattr__(name):
    """Lazy import for module attributes."""
    if name == "BaseBrute":
        from .core.bruteforce import BaseBrute
        return BaseBrute
    elif name == "MultiUserBrute":
        from .core.bruteforce import MultiUserBrute
        return MultiUserBrute
    elif name == "PasswordGenerator":
        from .core.generator import PasswordGenerator
        return PasswordGenerator
    elif name == "SmartWordlist":
        from .core.smart_wordlist import SmartWordlist
        return SmartWordlist
    elif name == "CredentialValidator":
        from .core.validator import CredentialValidator
        return CredentialValidator
    elif name == "SSHBrute":
        from .modules.ssh import SSHBrute
        return SSHBrute
    elif name == "FTPBrute":
        from .modules.ftp import FTPBrute
        return FTPBrute
    elif name == "HTTPBrute":
        from .modules.http import HTTPBrute
        return HTTPBrute
    elif name == "MySQLBrute":
        from .modules.mysql import MySQLBrute
        return MySQLBrute
    elif name == "SMTPBrute":
        from .modules.smtp import SMTPBrute
        return SMTPBrute
    elif name == "RedisBrute":
        from .modules.redis import RedisBrute
        return RedisBrute
    elif name == "PostgreSQLBrute":
        from .modules.postgresql import PostgreSQLBrute
        return PostgreSQLBrute
    elif name == "TelnetBrute":
        from .modules.telnet import TelnetBrute
        return TelnetBrute
    elif name == "SMBBrute":
        from .modules.smb import SMBBrute
        return SMBBrute
    elif name == "VNCBrute":
        from .modules.vnc import VNCBrute
        return VNCBrute
    elif name == "SNMPBrute":
        from .modules.snmp import SNMPBrute
        return SNMPBrute
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "BaseBrute",
    "MultiUserBrute",
    "PasswordGenerator",
    "SmartWordlist",
    "CredentialValidator",
    "SSHBrute",
    "FTPBrute",
    "HTTPBrute",
    "MySQLBrute",
    "SMTPBrute",
    "RedisBrute",
    "PostgreSQLBrute",
    "TelnetBrute",
    "SMBBrute",
    "VNCBrute",
    "SNMPBrute",
]
