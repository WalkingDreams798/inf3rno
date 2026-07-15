"""TUI Dashboard for Inf3rno."""

import os
import sys
import json
import time
import threading
from datetime import datetime
from typing import List, Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich import box

console = Console()


class Dashboard:
    """Interactive TUI Dashboard for Inf3rno."""

    def __init__(self):
        self.console = Console()
        self.attacks = []
        self.found_credentials = []
        self.is_running = False
        self.current_attack = None

    def print_banner(self):
        """Print the Inf3rno banner."""
        banner = """
[bold red]
    _____ _____ ____  __  __ ____  _     ___ _____ ____
   |_   _| ____|  _ \\|  \\/  |  _ \\| |   |_ _|_   _/ ___|
     | | |  _| | |_) | |\\/| | |_) | |    | |  | | \\___ \\
     | | | |___|  _ <| |  | |  __/| |___ | |  | |  ___) |
     |_| |_____|_| \\_\\_|  |_|_|   |_____|___| |_| |____/
[/bold red]
[cyan]    [ TUI Dashboard - Multi-Protocol Brute-Force Tool ][/cyan]
"""
        self.console.print(banner)

    def print_menu(self):
        """Print main menu."""
        menu = Table(show_header=False, box=box.ROUNDED, border_style="cyan")
        menu.add_column("No", style="bold yellow", width=5)
        menu.add_column("Option", style="bold white")
        menu.add_column("Description", style="dim")

        menu.add_row("1", "New Attack", "Start a new brute-force attack")
        menu.add_row("2", "View Attacks", "List all current attacks")
        menu.add_row("3", "View Credentials", "Show found credentials")
        menu.add_row("4", "Generate Wordlist", "Create smart wordlist")
        menu.add_row("5", "Scan Ports", "Scan common ports on target")
        menu.add_row("6", "Settings", "Configure default settings")
        menu.add_row("0", "Exit", "Exit the dashboard")

        self.console.print("\n[bold cyan]Main Menu[/bold cyan]")
        self.console.print(menu)

    def new_attack(self):
        """Create a new brute-force attack."""
        self.console.print("\n[bold yellow]New Attack Configuration[/bold yellow]")

        # Get target
        target = Prompt.ask("[cyan]Target IP/Hostname[/cyan]")

        # Get service
        services = Table(show_header=False, box=box.SIMPLE)
        services.add_column("No", style="bold yellow", width=5)
        services.add_column("Service", style="bold white")
        services.add_column("Default Port", style="dim")

        services.add_row("1", "SSH", "22")
        services.add_row("2", "FTP", "21")
        services.add_row("3", "HTTP", "80")
        services.add_row("4", "MySQL", "3306")
        services.add_row("5", "SMTP", "587")
        services.add_row("6", "Redis", "6379")
        services.add_row("7", "PostgreSQL", "5432")
        services.add_row("8", "Telnet", "23")

        self.console.print(services)
        service_choice = Prompt.ask("[cyan]Select service[/cyan]", choices=["1", "2", "3", "4", "5", "6", "7", "8"])

        service_map = {
            "1": ("SSH", 22),
            "2": ("FTP", 21),
            "3": ("HTTP", 80),
            "4": ("MySQL", 3306),
            "5": ("SMTP", 587),
            "6": ("Redis", 6379),
            "7": ("PostgreSQL", 5432),
            "8": ("Telnet", 23),
        }

        service_name, default_port = service_map[service_choice]
        port = Prompt.ask("[cyan]Port[/cyan]", default=str(default_port))

        # Get credentials
        username = Prompt.ask("[cyan]Username[/cyan]", default="admin")
        wordlist = Prompt.ask("[cyan]Wordlist path[/cyan]", default="wordlists/passwords.txt")

        # Get options
        threads = int(Prompt.ask("[cyan]Threads[/cyan]", default="5"))
        delay = float(Prompt.ask("[cyan]Delay (seconds)[/cyan]", default="0"))
        rate_limit = Confirm.ask("[cyan]Enable rate limit detection?[/cyan]", default=False)

        # Create attack config
        attack = {
            "id": len(self.attacks) + 1,
            "target": target,
            "service": service_name,
            "port": int(port),
            "username": username,
            "wordlist": wordlist,
            "threads": threads,
            "delay": delay,
            "rate_limit": rate_limit,
            "status": "pending",
            "started_at": None,
            "attempts": 0,
            "found": [],
        }

        self.attacks.append(attack)
        self.console.print(f"\n[bold green]Attack #{attack['id']} created![/bold green]")

        # Ask to start
        if Confirm.ask("[cyan]Start attack now?[/cyan]", default=True):
            self.start_attack(attack)

    def start_attack(self, attack: dict):
        """Start a brute-force attack."""
        attack["status"] = "running"
        attack["started_at"] = datetime.now().isoformat()

        self.console.print(f"\n[bold yellow]Starting Attack #{attack['id']}[/bold yellow]")
        self.console.print(f"  Target: {attack['target']}:{attack['port']}")
        self.console.print(f"  Service: {attack['service']}")
        self.console.print(f"  Username: {attack['username']}")

        # Build command
        cmd = f"python3 inf3rno/cli.py -t {attack['target']} --{attack['service'].lower()} "
        cmd += f"-u {attack['username']} -w {attack['wordlist']} "
        cmd += f"-T {attack['threads']} "

        if attack['delay'] > 0:
            cmd += f"--delay {attack['delay']} "
        if attack['rate_limit']:
            cmd += "--rate-limit "

        self.console.print(f"\n[dim]Command: {cmd}[/dim]\n")

        # Run in background thread
        def run_attack():
            try:
                import subprocess
                process = subprocess.Popen(
                    cmd.split(),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )

                for line in process.stdout:
                    self.console.print(f"  {line.strip()}")

                process.wait()
                attack["status"] = "completed"
            except Exception as e:
                attack["status"] = "failed"
                self.console.print(f"[red]Error: {e}[/red]")

        thread = threading.Thread(target=run_attack, daemon=True)
        thread.start()

    def view_attacks(self):
        """View all attacks."""
        if not self.attacks:
            self.console.print("[yellow]No attacks found.[/yellow]")
            return

        table = Table(title="Attacks", box=box.ROUNDED, border_style="cyan")
        table.add_column("ID", style="bold yellow", width=5)
        table.add_column("Target", style="bold white")
        table.add_column("Service", style="bold green")
        table.add_column("Status", style="bold")
        table.add_column("Attempts", style="dim")

        for attack in self.attacks:
            status_style = {
                "pending": "yellow",
                "running": "green",
                "completed": "blue",
                "failed": "red",
            }.get(attack["status"], "white")

            table.add_row(
                str(attack["id"]),
                f"{attack['target']}:{attack['port']}",
                attack["service"],
                f"[{status_style}]{attack['status']}[/{status_style}]",
                str(attack["attempts"]),
            )

        self.console.print(table)

    def view_credentials(self):
        """View found credentials."""
        # Load from output/Found.txt
        found_file = "output/Found.txt"
        credentials = []

        if os.path.exists(found_file):
            with open(found_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if ":" in line:
                        username, password = line.split(":", 1)
                        credentials.append({"username": username, "password": password})

        if not credentials:
            self.console.print("[yellow]No credentials found.[/yellow]")
            return

        table = Table(title="Found Credentials", box=box.ROUNDED, border_style="green")
        table.add_column("#", style="bold yellow", width=5)
        table.add_column("Username", style="bold white")
        table.add_column("Password", style="bold green")

        for i, cred in enumerate(credentials, 1):
            table.add_row(str(i), cred["username"], cred["password"])

        self.console.print(table)

    def generate_wordlist(self):
        """Generate smart wordlist."""
        self.console.print("\n[bold yellow]Smart Wordlist Generator[/bold yellow]")

        target = Prompt.ask("[cyan]Target[/cyan]", default="localhost")
        username = Prompt.ask("[cyan]Username[/cyan]", default="admin")
        output_file = Prompt.ask("[cyan]Output file[/cyan]", default="output/smart_wordlist.txt")

        cmd = f"python3 inf3rno/cli.py -t {target} -u {username} --smart --save-gen {output_file}"

        self.console.print(f"\n[dim]Command: {cmd}[/dim]\n")

        if Confirm.ask("[cyan]Generate wordlist?[/cyan]", default=True):
            import subprocess
            subprocess.run(cmd.split())

    def scan_ports(self):
        """Scan common ports."""
        self.console.print("\n[bold yellow]Port Scanner[/bold yellow]")

        target = Prompt.ask("[cyan]Target[/cyan]")

        cmd = f"python3 inf3rno/cli.py -t {target} --list"

        self.console.print(f"\n[dim]Command: {cmd}[/dim]\n")

        import subprocess
        subprocess.run(cmd.split())

    def settings(self):
        """Configure settings."""
        self.console.print("\n[bold yellow]Settings[/bold yellow]")

        table = Table(show_header=False, box=box.ROUNDED, border_style="cyan")
        table.add_column("Setting", style="bold white")
        table.add_column("Value", style="bold yellow")

        table.add_row("Default Threads", "5")
        table.add_row("Default Delay", "0")
        table.add_row("Rate Limit", "Disabled")
        table.add_row("Wordlist", "wordlists/passwords.txt")

        self.console.print(table)

    def run(self):
        """Run the TUI dashboard."""
        self.print_banner()

        while True:
            self.print_menu()
            choice = Prompt.ask("\n[bold cyan]Select option[/bold cyan]")

            if choice == "1":
                self.new_attack()
            elif choice == "2":
                self.view_attacks()
            elif choice == "3":
                self.view_credentials()
            elif choice == "4":
                self.generate_wordlist()
            elif choice == "5":
                self.scan_ports()
            elif choice == "6":
                self.settings()
            elif choice == "0":
                self.console.print("\n[bold red]Exiting...[/bold red]")
                break
            else:
                self.console.print("[red]Invalid option![/red]")

            self.console.print()


def main():
    """Main entry point for TUI."""
    dashboard = Dashboard()
    dashboard.run()


if __name__ == "__main__":
    main()
