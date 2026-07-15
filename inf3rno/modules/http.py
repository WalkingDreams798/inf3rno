"""HTTP brute-force module."""

import requests
from inf3rno.core.bruteforce import BaseBrute


class HTTPBrute(BaseBrute):
    """HTTP form/basic auth brute-force implementation."""

    def __init__(self, target: str, port: int = 80, username: str = "admin",
                 wordlist: str = "wordlists/passwords.txt", threads: int = 5,
                 output_file: str = None, verbose: bool = False,
                 delay: float = 0.0, proxy: str = None,
                 login_url: str = None, fail_string: str = None,
                 method: str = "basic"):
        super().__init__(target, port, username, wordlist, threads, output_file, verbose, delay, proxy)
        self.service = "HTTP"
        self.login_url = login_url
        self.fail_string = fail_string or "Invalid"
        self.method = method
        self.session = requests.Session()

        # Configure proxy
        if self.proxy:
            self.session.proxies = {
                "http": self.proxy,
                "https": self.proxy,
            }

    def try_login(self, username: str, password: str) -> bool:
        """Attempt HTTP login."""
        try:
            if self.method == "basic":
                url = f"http://{self.target}:{self.port}/"
                response = self.session.get(
                    url,
                    auth=(username, password),
                    timeout=5,
                    allow_redirects=False,
                )
                return response.status_code != 401

            elif self.method == "form":
                if not self.login_url:
                    print("[!] Login URL required for form-based auth")
                    return False

                data = {
                    "username": username,
                    "user": username,
                    "email": username,
                    "password": password,
                    "pass": password,
                }

                response = self.session.post(
                    self.login_url,
                    data=data,
                    timeout=5,
                    allow_redirects=True,
                )

                if self.fail_string.lower() not in response.text.lower():
                    return True
                return False

            else:
                print(f"[!] Unknown HTTP method: {self.method}")
                return False

        except requests.RequestException as e:
            if self.verbose:
                print(f"[!] HTTP error for {username}:{password}: {e}")
            return False

        except Exception as e:
            if self.verbose:
                print(f"[!] Error: {e}")
            return False
