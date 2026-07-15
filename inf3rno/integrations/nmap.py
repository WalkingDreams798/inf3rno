"""Nmap integration module for Inf3rno."""

import os
import subprocess
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional


class NmapIntegration:
    """Nmap integration for port scanning and service detection."""

    def __init__(self):
        self.nmap_path = self._find_nmap()

    def _find_nmap(self) -> Optional[str]:
        """Find nmap executable path."""
        try:
            result = subprocess.run(
                ["which", "nmap"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass

        # Common paths
        common_paths = [
            "/usr/bin/nmap",
            "/usr/local/bin/nmap",
            "/opt/nmap/nmap",
        ]
        for path in common_paths:
            if os.path.exists(path):
                return path

        return None

    def is_available(self) -> bool:
        """Check if nmap is available."""
        return self.nmap_path is not None

    def quick_scan(self, target: str, ports: str = None) -> Dict:
        """
        Quick scan common ports.

        Args:
            target: Target IP or hostname
            ports: Port range (e.g., "22,80,443" or "1-1000")

        Returns:
            Dictionary with scan results
        """
        if not self.is_available():
            return {"error": "Nmap not found"}

        cmd = [self.nmap_path, "-T4", "--open"]

        if ports:
            cmd.extend(["-p", ports])
        else:
            cmd.extend(["-p", "21,22,23,25,80,110,135,139,143,443,445,993,995,1433,3306,3389,5432,5900,6379,8080,8443"])

        cmd.extend(["-oX", "-", target])

        return self._run_scan(cmd)

    def service_scan(self, target: str, ports: str = None) -> Dict:
        """
        Service version detection scan.

        Args:
            target: Target IP or hostname
            ports: Port range

        Returns:
            Dictionary with scan results
        """
        if not self.is_available():
            return {"error": "Nmap not found"}

        cmd = [self.nmap_path, "-sV", "-T4", "--open"]

        if ports:
            cmd.extend(["-p", ports])

        cmd.extend(["-oX", "-", target])

        return self._run_scan(cmd)

    def full_scan(self, target: str) -> Dict:
        """
        Full port scan (1-65535).

        Args:
            target: Target IP or hostname

        Returns:
            Dictionary with scan results
        """
        if not self.is_available():
            return {"error": "Nmap not found"}

        cmd = [
            self.nmap_path,
            "-p-",
            "-T4",
            "--open",
            "-oX",
            "-",
            target,
        ]

        return self._run_scan(cmd)

    def vuln_scan(self, target: str) -> Dict:
        """
        Vulnerability scan using Nmap scripts.

        Args:
            target: Target IP or hostname

        Returns:
            Dictionary with scan results
        """
        if not self.is_available():
            return {"error": "Nmap not found"}

        cmd = [
            self.nmap_path,
            "--script",
            "vuln",
            "-T4",
            "-oX",
            "-",
            target,
        ]

        return self._run_scan(cmd)

    def ssh_scan(self, target: str) -> Dict:
        """
        SSH-specific scan.

        Args:
            target: Target IP or hostname

        Returns:
            Dictionary with scan results
        """
        if not self.is_available():
            return {"error": "Nmap not found"}

        cmd = [
            self.nmap_path,
            "-p", "22",
            "--script",
            "ssh2-enum-algos,ssh-hostkey,ssh-auth-methods",
            "-T4",
            "-oX",
            "-",
            target,
        ]

        return self._run_scan(cmd)

    def ftp_scan(self, target: str) -> Dict:
        """
        FTP-specific scan.

        Args:
            target: Target IP or hostname

        Returns:
            Dictionary with scan results
        """
        if not self.is_available():
            return {"error": "Nmap not found"}

        cmd = [
            self.nmap_path,
            "-p", "21",
            "--script",
            "ftp-anon,ftp-bounce,ftp-syst,ftp-vsftpd-backdoor,ftp-proftpd-backdoor",
            "-T4",
            "-oX",
            "-",
            target,
        ]

        return self._run_scan(cmd)

    def smb_scan(self, target: str) -> Dict:
        """
        SMB-specific scan.

        Args:
            target: Target IP or hostname

        Returns:
            Dictionary with scan results
        """
        if not self.is_available():
            return {"error": "Nmap not found"}

        cmd = [
            self.nmap_path,
            "-p", "139,445",
            "--script",
            "smb-enum-shares,smb-enum-users,smb-os-discovery,smb-security-mode",
            "-T4",
            "-oX",
            "-",
            target,
        ]

        return self._run_scan(cmd)

    def http_scan(self, target: str, ports: str = "80,443,8080,8443") -> Dict:
        """
        HTTP-specific scan.

        Args:
            target: Target IP or hostname
            ports: HTTP ports to scan

        Returns:
            Dictionary with scan results
        """
        if not self.is_available():
            return {"error": "Nmap not found"}

        cmd = [
            self.nmap_path,
            "-p", ports,
            "--script",
            "http-enum,http-headers,http-methods,http-title",
            "-T4",
            "-oX",
            "-",
            target,
        ]

        return self._run_scan(cmd)

    def _run_scan(self, cmd: List[str]) -> Dict:
        """Run nmap scan and parse results."""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode != 0 and not result.stdout:
                return {"error": result.stderr}

            return self._parse_xml(result.stdout)

        except subprocess.TimeoutExpired:
            return {"error": "Scan timed out (5 minutes)"}
        except Exception as e:
            return {"error": str(e)}

    def _parse_xml(self, xml_output: str) -> Dict:
        """Parse nmap XML output."""
        try:
            root = ET.fromstring(xml_output)

            scan_info = {
                "scanner": "nmap",
                "args": root.get("args", ""),
                "start_time": root.get("start", ""),
            }

            hosts = []
            for host in root.findall(".//host"):
                host_data = {}

                # Get IP
                addr = host.find("address[@addrtype='ipv4']")
                if addr is not None:
                    host_data["ip"] = addr.get("addr", "")

                # Get hostname
                hostname = host.find(".//hostname")
                if hostname is not None:
                    host_data["hostname"] = hostname.get("name", "")

                # Get state
                state = host.find("status")
                if state is not None:
                    host_data["state"] = state.get("state", "")

                # Get ports
                ports = []
                for port_elem in host.findall(".//port"):
                    port_data = {
                        "port": int(port_elem.get("portid", 0)),
                        "protocol": port_elem.get("protocol", "tcp"),
                    }

                    state_elem = port_elem.find("state")
                    if state_elem is not None:
                        port_data["state"] = state_elem.get("state", "")

                    service = port_elem.find("service")
                    if service is not None:
                        port_data["service"] = {
                            "name": service.get("name", ""),
                            "product": service.get("product", ""),
                            "version": service.get("version", ""),
                            "extrainfo": service.get("extrainfo", ""),
                        }

                    # Get scripts
                    scripts = []
                    for script in port_elem.findall("script"):
                        scripts.append({
                            "id": script.get("id", ""),
                            "output": script.get("output", ""),
                        })
                    if scripts:
                        port_data["scripts"] = scripts

                    ports.append(port_data)

                host_data["ports"] = ports
                hosts.append(host_data)

            return {
                "scan_info": scan_info,
                "hosts": hosts,
                "total_hosts": len(hosts),
            }

        except ET.ParseError as e:
            return {"error": f"XML parse error: {e}"}

    def scan_to_bruteforce(self, target: str) -> List[Dict]:
        """
        Scan target and return services suitable for brute-force.

        Args:
            target: Target IP or hostname

        Returns:
            List of services that can be brute-forced
        """
        result = self.service_scan(target)

        if "error" in result:
            return []

        bruteforce_services = {
            "ssh": {"module": "ssh", "default_user": "root"},
            "ftp": {"module": "ftp", "default_user": "anonymous"},
            "http": {"module": "http", "default_user": "admin"},
            "mysql": {"module": "mysql", "default_user": "root"},
            "smtp": {"module": "smtp", "default_user": "admin"},
            "redis": {"module": "redis", "default_user": "default"},
            "postgresql": {"module": "postgresql", "default_user": "postgres"},
            "telnet": {"module": "telnet", "default_user": "admin"},
            "microsoft-ds": {"module": "smb", "default_user": "Administrator"},
            "netbios-ssn": {"module": "smb", "default_user": "Administrator"},
            "vnc": {"module": "vnc", "default_user": ""},
            "snmp": {"module": "snmp", "default_user": "public"},
            "ms-wbt-server": {"module": "rdp", "default_user": "Administrator"},
        }

        services = []
        for host in result.get("hosts", []):
            for port_data in host.get("ports", []):
                service_name = port_data.get("service", {}).get("name", "")
                if service_name in bruteforce_services:
                    service_info = bruteforce_services[service_name]
                    services.append({
                        "host": host.get("ip", target),
                        "port": port_data.get("port"),
                        "service": service_name,
                        "module": service_info["module"],
                        "default_user": service_info["default_user"],
                        "product": port_data.get("service", {}).get("product", ""),
                        "version": port_data.get("service", {}).get("version", ""),
                    })

        return services


# Global instance
nmap_integration = NmapIntegration()
