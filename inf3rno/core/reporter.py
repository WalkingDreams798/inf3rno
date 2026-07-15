"""Reporter and export module."""

import os
import json
import csv
import time
from datetime import datetime
from typing import Optional, List, Tuple

from colorama import Fore, Style, init

init(autoreset=True)


class Colors:
    """Color constants."""
    RED = Fore.RED
    GREEN = Fore.GREEN
    YELLOW = Fore.YELLOW
    BLUE = Fore.BLUE
    CYAN = Fore.CYAN
    WHITE = Fore.WHITE
    RESET = Style.RESET_ALL
    BRIGHT = Style.BRIGHT


class Reporter:
    """Handles output formatting and logging."""

    def __init__(self, verbose: bool = False, output_file: Optional[str] = None):
        self.verbose = verbose
        self.output_file = output_file
        self.start_time = None
        self.attempts = 0
        self.found = []
        self.log_file = None

        if output_file:
            log_dir = os.path.dirname(output_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
            log_path = output_file.replace(".txt", "_log.txt")
            self.log_file = open(log_path, "w")

    def start(self):
        """Start the timer."""
        self.start_time = time.time()

    def info(self, message: str):
        """Print info message."""
        print(f"{Colors.CYAN}[*]{Colors.RESET} {message}")

    def success(self, message: str):
        """Print success message."""
        print(f"{Colors.GREEN}[+]{Colors.RESET} {message}")

    def error(self, message: str):
        """Print error message."""
        print(f"{Colors.RED}[-]{Colors.RESET} {message}")

    def warning(self, message: str):
        """Print warning message."""
        print(f"{Colors.YELLOW}[!]{Colors.RESET} {message}")

    def attempt(self, username: str, password: str, success: bool):
        """Log an attempt."""
        self.attempts += 1

        if success:
            self.found.append((username, password))
            self.success(f"FOUND: {username}:{password}")
            self._save_credential(username, password)
        elif self.verbose:
            self.error(f"Failed: {username}:{password}")

        if self.log_file:
            status = "SUCCESS" if success else "FAILED"
            self.log_file.write(
                f"[{datetime.now().isoformat()}] {status}: {username}:{password}\n"
            )

    def _save_credential(self, username: str, password: str):
        """Save found credential to file."""
        if self.output_file:
            with open(self.output_file, "a") as f:
                f.write(f"{username}:{password}\n")
        else:
            os.makedirs("output", exist_ok=True)
            with open("output/Found.txt", "a") as f:
                f.write(f"{username}:{password}\n")

    def summary(self):
        """Print final summary."""
        elapsed = time.time() - self.start_time if self.start_time else 0

        print(f"\n{Colors.CYAN}{'='*50}{Colors.RESET}")
        print(f"{Colors.CYAN}[*] SUMMARY{Colors.RESET}")
        print(f"{Colors.CYAN}{'='*50}{Colors.RESET}")
        print(f"{Colors.WHITE}Time elapsed:{Colors.RESET} {elapsed:.2f}s")
        print(f"{Colors.WHITE}Attempts:{Colors.RESET} {self.attempts}")

        if self.found:
            print(f"\n{Colors.GREEN}[+] Found {len(self.found)} valid credential(s):{Colors.RESET}")
            for user, pwd in self.found:
                print(f"    {Colors.GREEN}{user}:{pwd}{Colors.RESET}")
        else:
            print(f"\n{Colors.RED}[-] No valid credentials found.{Colors.RESET}")

        print(f"{Colors.CYAN}{'='*50}{Colors.RESET}\n")

    def close(self):
        """Close log file."""
        if self.log_file:
            self.log_file.close()


class ReportExporter:
    """Export brute-force results to various formats."""

    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def export_json(self, found: List[Tuple[str, str]], filename: str = "report.json",
                    target: str = "", port: int = 0, service: str = ""):
        """Export results to JSON."""
        filepath = os.path.join(self.output_dir, filename)

        data = {
            "tool": "Inf3rno",
            "timestamp": datetime.now().isoformat(),
            "target": target,
            "port": port,
            "service": service,
            "total_found": len(found),
            "credentials": [
                {"username": user, "password": pwd}
                for user, pwd in found
            ]
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        print(f"[*] JSON report saved: {filepath}")
        return filepath

    def export_csv(self, found: List[Tuple[str, str]], filename: str = "report.csv"):
        """Export results to CSV."""
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Username", "Password"])
            for user, pwd in found:
                writer.writerow([user, pwd])

        print(f"[*] CSV report saved: {filepath}")
        return filepath

    def export_html(self, found: List[Tuple[str, str]], filename: str = "report.html",
                    target: str = "", port: int = 0, service: str = ""):
        """Export results to HTML."""
        filepath = os.path.join(self.output_dir, filename)

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Inf3rno Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #1a1a2e; color: #eee; }}
        .header {{ background: #16213e; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
        .header h1 {{ color: #e94560; margin: 0; }}
        .info {{ background: #0f3460; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .info p {{ margin: 5px 0; }}
        table {{ width: 100%; border-collapse: collapse; background: #16213e; border-radius: 10px; overflow: hidden; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #0f3460; }}
        th {{ background: #e94560; color: white; }}
        tr:hover {{ background: #0f3460; }}
        .found {{ color: #4ecca3; font-weight: bold; }}
        .footer {{ margin-top: 20px; text-align: center; color: #666; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Inf3rno Report</h1>
    </div>
    <div class="info">
        <p><strong>Target:</strong> {target}:{port}</p>
        <p><strong>Service:</strong> {service}</p>
        <p><strong>Generated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        <p><strong>Credentials Found:</strong> <span class="found">{len(found)}</span></p>
    </div>
    <table>
        <thead>
            <tr>
                <th>#</th>
                <th>Username</th>
                <th>Password</th>
            </tr>
        </thead>
        <tbody>
"""

        for i, (user, pwd) in enumerate(found, 1):
            html += f"""            <tr>
                <td>{i}</td>
                <td>{user}</td>
                <td>{pwd}</td>
            </tr>
"""

        html += """        </tbody>
    </table>
    <div class="footer">
        <p>Generated by Inf3rno - Multi-Protocol Brute-Force Tool</p>
    </div>
</body>
</html>"""

        with open(filepath, "w") as f:
            f.write(html)

        print(f"[*] HTML report saved: {filepath}")
        return filepath

    def export_all(self, found: List[Tuple[str, str]], target: str = "",
                   port: int = 0, service: str = ""):
        """Export to all formats."""
        if not found:
            print("[-] No credentials to export")
            return

        self.export_json(found, target=target, port=port, service=service)
        self.export_csv(found)
        self.export_html(found, target=target, port=port, service=service)
